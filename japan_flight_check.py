import datetime
import urllib2
import json
import time
from make_email import *
from collections import namedtuple
from operator import attrgetter

# QPX Express limits to 50 free queries per day
global MAX_QUERIES
MAX_QUERIES = 20

def search_flights(config_file, recipient, key_path, pw_path):
    """Searches for flights and sends an email with the results.

    Generates and sends a QPX Express query for flights with the parameters
        from config_file, then sends the results to the recipient email address.

    Args:
        config_file: string, the path to a file with the desired flight
            parameters.

            Must be in the following format:

                DEPARTURE_PORT = City
                ARRIVAL_PORT = City
                DEPARTURE_DATE = Date
                TRIP_LENGTH = Integer

            and may contain the following optional fields:

                MAX_COST = Integer
                VARY_BY_DAYS = Integer
                MAX_DURATION = Integer
                MAX_FLIGHTS = Integer

            where the values are as follows:

                DEPARTURE_PORT: string, the three-letter airport or city codes
                    from which to depart.
                    To search multiple city codes, use spaces as separators.
                    (Example: DEPARTURE_PORT = ORD IND)

                ARRIVAL_PORT: string, the three-letter airport or city code
                    of the desired destination city.
                    To search multiple city codes, use spaces as separators.
                    (Example: ARRIVAL_PORT = TYO OSA)

                DEPARTURE_DATE: string, the desired departure date
                    in YYYY-MM-DD format. 
                    Must be a valid date no earlier than the current date.
                    To allow variance in the departure date, use the following
                    parameter, VARY_BY_DAYS.

                TRIP_LENGTH: integer, the desired duration of the trip in days.
                    Must be greater than 0.
                    To allow variance in the departure date, use the following
                    parameter, VARY_BY_DAYS.

                VARY_BY_DAYS: integer, the number of days to allow variance in
                    the departure date and trip length.
                    (Example: To allow leaving up to 3 days sooner or later than
                    DEPARTURE_DATE, and staying 3 days more or less than
                    TRIP_LENGTH, enter 3.

                MAX_COST: integer, the maximum price, in whole dollars, to
                    allow in search results.  Must be greater than 0.
                    For example, to limit shown flights to $1000.00, MAX_COST
                    should be 1000 (no $, decimal, or cent values).

                MAX_DURATION: integer, the maximum flight length, in minutes,
                    to allow in search results. Must be greater than 0.

                MAX_FLIGHTS: integer, the maximum number of flights to show
                    in the results. Flights are first selected by the above
                    parameters, sorted by price, and then returned.
                    Must be greater or equal to 0.

                Comments can be marked with a # as the first character of each
                    comment line. This is required even if the line is otherwise
                    blank.

        recipient: string, the email address to which to send the results.
            Must be a valid email address.

        key_path: string, the system path address where the QPX Express API
            key can be found. The key must be in a text file by itself.

        pw_path: string, the system path address where the Gmail account's
            password can be found.
            The password must be in a text file by itself.

    Raises:
        ValueError: One or more parameters are not correctly formatted.
    """
    flights = []
    config = _parse_config_file(config_file)
    queries = _create_queries(config)
    for query in queries:
        flights.extend(_parse_flights(send_request(query, key_path)))
    best_flights = sorted(flights, key=lambda x: float(x.price))
    if "MAX_FLIGHTS" in config:
        best_flights = best_flights[:config["MAX_FLIGHTS"]]
    # Max duration is optional, and passing None for it is accepted behavior
    formatted = print_flights(best_flights, config.get("MAX_DURATION"))
    email = create_email(formatted, recipient)
    send_email(email, pw_path)

def _create_queries(config):
    """Creates a list of queries given a configuration."""
    queries = []
    variance = config["VARY_BY_DAYS"]
    for dep_city in config["DEPARTURE_PORT"]:
        for arr_city in config["ARRIVAL_PORT"]:
            # Try departure dates +- variance days, starting with variance days
            # before the date and looping up to variance days after
            for v_date in xrange(-variance, variance + 1):
                query_date = _calculate_date(config["DEPARTURE_DATE"], v_date)
                for v_len in xrange(-variance, variance + 1):
                    if len(queries) >= MAX_QUERIES:
                        return queries
                    # Max cost and max flights are optional,
                    # so use get to avoid a KeyError
                    # MAX_FLIGHTS actually refers to the total number of flight
                    # results to return, but since all the best flights could
                    # result from a single query, use it as an upper bound
                    # for each query.
                    query = build_query(dep_city, arr_city, query_date,
                        config["TRIP_LENGTH"] + v_len, config.get("MAX_COST"),
                        config.get("MAX_FLIGHTS"))
                    queries.append(query)
    # Simple queries may not reach the query limit
    return queries

def _parse_config_file(config_file):
    """Parses a config file for searching multiple types of flights."""
    # See search_flights for config file format.
    config_info = []
    with open(config_file, "r") as input_file:
        config_info = input_file.readlines()
    # The expected data in config files, split into text and numerical
    # parameters for converting.
    # The date contains numbers, but is formatted as a string (YYYY-MM-DD)
    TEXT_PARAMS = ("DEPARTURE_PORT", "ARRIVAL_PORT", "DEPARTURE_DATE")
    NUM_PARAMS = ("TRIP_LENGTH", "VARY_BY_DAYS", "MAX_COST", "MAX_DURATION",
            "MAX_FLIGHTS")
    config_settings = {}
    for line in config_info:
        if line[0] == "#":
            # Comment line
            continue
        setting, value = map(str.strip, line.split("="))
        if setting in TEXT_PARAMS:
            if setting in ("DEPARTURE_PORT", "ARRIVAL_PORT"):
                # These two parameters may or may not have multiple values
                config_settings[setting] = value.split()
            else:
                config_settings[setting] = value
        elif setting in NUM_PARAMS:
            # MAX_COST could be given as a float, but the specification states
            # that it must be an integer, so we can convert it as such
            config_settings[setting] = int(value)
    return config_settings

def send_request(query, key_path):
    """Sends a flight query to the QPX Server.

    Using a query string from build_query, sends an HTTP request to the QPX
    server and returns the response.

    Limited to 50 queries per day.

    Args:
        query: string, JSON-formatted data generated by build_query.

    Returns:
        A string containing the JSON-formatted data of the search results.
    """
    base_url = "https://www.googleapis.com/qpxExpress/v1/trips/search?key="
    url = base_url + _get_auth_key(key_path)
    request = urllib2.Request(url, query, 
            {'Content-Type': 'application/json', 'Content-Length': len(query)})
    response_page = urllib2.urlopen(request)
    response = response_page.read()
    response_page.close()
    return response

Flight = namedtuple('Flight', 'price legs')
Leg = namedtuple('Leg',
    'origin destination dep_time arr_time carrier flight_num duration')

def _parse_flights(result):
    """Converts result data from JSON string into Flight namedtuples."""
    flight_data = json.loads(result)
    # flight_data is a dict with unicode keys:
    # 'trips' > 'tripOption' > 'saleTotal'
    # 'trips' > 'tripOption' > 'slice' > (list of flights)
    # (list of flights) > 'segment' > 'leg' > (list of legs)
    # (list of legs) > 'departureTime', 'arrivalTime', 'origin', 'destination'
    # (list of flights) > 'segment' > 'flight' > 'carrier, 'number'
    flights = []
    for flight in flight_data[u'trips'][u'tripOption']:
        # If currency is not stripped, a ValueError will result when trying to
        #    convert prices to floats for sorting
        if "USD" not in flight[u'saleTotal']:
            raise ValueError("Flights must be in USD")
        price = flight[u'saleTotal'].replace("USD", "")
        legs = []
        for flight_slice in flight[u'slice']:
            duration = flight_slice[u'duration']
            for leg in flight_slice[u'segment']:
                carrier = leg[u'flight'][u'carrier']
                flight_num = leg[u'flight'][u'number']
                leg_data = leg[u'leg'][0]
                dep_time = leg_data[u'departureTime']
                arr_time = leg_data[u'arrivalTime']
                origin = leg_data[u'origin']
                arr_port = leg_data[u'destination']
                legs.append(Leg(origin, arr_port, dep_time, arr_time, carrier,
                    flight_num, duration))
        # Omit flights with airport transfers
        if _has_airport_transfer(legs):
            continue
        flights.append(Flight(price, legs))
    return flights

def _has_airport_transfer(legs):
    """Returns True if this flight involves transferring airports."""
    for i in xrange(1, len(legs)):
        if legs[i].origin != legs[i-1].destination:
            return True
    return False

def print_flights(flights, max_duration=None):
    """Converts a formatted list of Flights into a human readable string.

         Format:
         Price: (price) (Departure date) to (Return date)
             Leg 1:
                 Number: (Carrier, Flight No.)    Total duration
                 Departure from (port) at (time)    Arrives at (port) at (time)
             Leg 2: (same format as Leg 1)
             ...

        Args:
            flights: list of Flight namedtuples to print.

            max_duration: integer, the maximum flight length, in minutes,
                to include in search results. Must be greater than 0.

                Defaults to None, which shows flights of all lengths.
 
        Raises:
            ValueError: max_duration is <= 0.

        Returns:
            A formatted string containing flight data and text separators.
    """
    output = ""
    for flight in flights:
        # Skip flights longer than max_duration (in minutes)
        if max_duration is not None:
            if max_duration <= 0:
                raise ValueError("Max duration must be greater than 0")
            if any(map(lambda x: x.duration > max_duration, flight.legs)):
                continue
        # Dates/times are in format 2017-04-01T00:30-05:00
        # strptime does not recognize this timezone format, so find
        # and ignore the timezone portion, then replace the T with a space
        # for better readability
        # Time zone will be + or - some number of hours
        tzone_loc = flight.legs[0].dep_time.rfind("+")
        if tzone_loc == -1:
            tzone_loc = flight.legs[0].dep_time.rfind("-")
        d_date = flight.legs[0].dep_time[:tzone_loc].replace("T", " ")
        # Note: Return date is based on return arrival time,
        #       not departure from destination time, so may not match
        #       flight dates.
        r_date = flight.legs[-1].arr_time[:tzone_loc].replace("T", " ")
        output += "Price: {}\t{} to {}\n".format(flight.price, d_date, r_date)
        for i in xrange(len(flight.legs)):
            output += "\tLeg {}:\n".format(i + 1)
            leg = flight.legs[i]
            output += "\t\tNumber: {}{}".format(leg.carrier, leg.flight_num)
            duration = "{} hr {} min".format(*divmod(int(leg.duration), 60))
            output += "\tTotal duration: {}\n".format(duration)
            output += "\t\tDeparture: {} at {}\t Arrival: {} at {}".format(
                 leg.origin, leg.dep_time, leg.destination, leg.arr_time)
            output += "\n\n"
        output += ("*" * 90) + "\n"
    return output

def _get_auth_key(path=None):
    """Fetches an authorization key stored elsewhere on the file system.

    This key is used for communicating with the QPX server, and is stored
    separately from the code for security reasons.

    Args:
        path: string, the full pathname (including filename) of the file
            containing the authorization key.

    Returns:
        string, the authorization key for the QPX server.
    """
    loc = DEFAULT_PATH if not path else path
    key = ""
    with open(loc, 'r') as input_file:
        key = input_file.read().strip()
    return key

def build_query(dep_port="CHI", arr_port="TYO", dep_date="2017-04-01", 
        trip_length=90, max_cost=None, max_flights=None):
    """Builds a JSON query for checking flights on QPX."""
    # Error checking
    for code in dep_port, arr_port:
        if len(code) != 3:
            raise ValueError("Invalid city or airport code: {}".format(code))
    search_date = time.strptime(dep_date, "%Y-%m-%d")
    # strptime creates a struct_time object and date.today creates
    # a datetime.date object, so convert with date.timetuple for comparison
    if search_date < datetime.date.timetuple(datetime.date.today()):
        raise ValueError("Departure date may not be in the past")
    if trip_length <= 0:
        raise ValueError("Trip length must be greater than 0")
    if max_cost is not None and max_cost <= 0:
        raise ValueError("Max cost, if given, must be greater than 0")
    if max_flights is not None and max_flights <= 0:
        raise ValueError("Max flights, if given, must be greater than 0")
    json_query = ""
    with open("base_query.json", "r") as raw_file:
        json_query = json.load(raw_file)
    # JSON query is in the following format:
    # {"request":
    #   {"refundable": false, "passengers": {"adultCount": 1},
    #   "slice": [{"origin": "A", "date": "2017-04-01", "destination": "B"},
    #             {"origin": "B", "date": "2017-06-30", "destination": "A"}],
    #   "solutions": 5, "maxPrice": "USD1.00"
    #   }
    # }

    # Change cities
    json_query["request"]["slice"][0]["origin"] = unicode(dep_port)
    json_query["request"]["slice"][1]["origin"] = unicode(arr_port)
    json_query["request"]["slice"][0]["destination"] = unicode(arr_port)
    json_query["request"]["slice"][1]["destination"] = unicode(dep_port)
    # Change dates
    return_date = _calculate_date(dep_date, trip_length)
    json_query["request"]["slice"][0]["date"] = unicode(dep_date)
    json_query["request"]["slice"][1]["date"] = unicode(return_date)
    if max_cost:
        # Format to show dollars and cents
        json_query["request"]["maxPrice"] = u"USD{:.2f}".format(max_cost)
    if max_flights:
        json_query["request"]["solutions"] = int(max_flights)
    return json.dumps(json_query)

def _calculate_date(start_date, duration):
    """Calculates a later date given a start date and duration."""
    # We need a datetime object in order to add a timedelta to a date.
    # The first three parameters of datetime's constructor are Y/M/D,
    # which are the three pieces of data we need for this function.
    start_date = datetime.datetime(*time.strptime(start_date, "%Y-%m-%d")[:3])
    new_date = start_date + datetime.timedelta(duration)
    return new_date.strftime("%Y-%m-%d")
