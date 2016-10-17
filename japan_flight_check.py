import datetime
import urllib2
import json
from make_email import *
from collections import namedtuple

def _parse_config_file(config_file):
    """Parses a config file for searching multiple types of flights."""
    config_info = []
    with open(config_file, "r") as input_file:
        config_info = config_file.readlines()
    config_settings = {}
    # Expected data in config files
    PARAMS = ["DEPARTURE_PORT", "ARRIVAL_PORT", "DEPARTURE_DATE", 
            "TRIP_LENGTH", "VARY_BY_DAYS", "MAX_COST", "MAX_DURATION"]
    for i in xrange(len(config_info)):
        line = config_info[i]
        if not line.starts_with(PARAMS[i]):
            raise ValueError(
                    "Improperly formatted config file: see line {}".format(i+1))
        # Line should have one '=', so keep the second half of the line
        line_value = line.strip().split("=")[1].strip()
        if i < 2:
            # Only the first two lines allow multiple options
            config_settings[PARAMS[i]] = line_value.split()
        elif i == 2:
            # Departure date does not need splitting or converting here
            config_settings[PARAMS[i]] = line_value
        else:
            config_settings[PARAMS[i]] = int(line_value)
    return config_settings

# TODO: Combine all queries into one before sorting/sending
def search_flights(config_file, recipient):
#def search_flights(recipient, dep_port="CHI", arr_port="TYO",
        #dep_date="2017-04-01", trip_length=90, max_cost=900, max_duration=None):
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
                VARY_BY_DAYS = Integer
                MAX_COST = Integer
                MAX_DURATION = Integer

            where the values are as follows:

                DEPARTURE_PORT = string, the three-letter airport or city codes
                    from which to depart.
                    To search multiple city codes, use spaces as separators.
                    (Example: DEPARTURE_PORT = ORD IND)

                ARRIVAL_PORT = string, the three-letter airport or city code
                    of the desired destination city.
                    To search multiple city codes, use spaces as separators.
                    (Example: ARRIVAL_PORT = TYO OSA)

                DEPARTURE_DATE = string, the desired departure date
                    in YYYY-MM-DD format. 
                    Must be a valid date no earlier than the current date.
                    To allow variance in the departure date, use the following
                    parameter, VARY_BY_DAYS.

                TRIP_LENGTH = integer, the desired duration of the trip in days.
                    Must be greater than 0.
                    To allow variance in the departure date, use the following
                    parameter, VARY_BY_DAYS.

                VARY_BY_DAYS = integer, the number of days to allow variance in
                    the departure date and trip length.
                    (Example: To allow leaving up to 3 days sooner or later than
                    DEPARTURE_DATE, and staying 3 days more or less than
                    TRIP_LENGTH, enter 3.

                MAX_COST = integer, the maximum price, in dollars, to allow in search
            results.  Must be greater than 0.
                MAX_DURATION = 1200

        recipient: string, the email address to which to send the results.
            Must be a valid email address.


            Defaults to 900.

        max_duration: integer, the maximum flight length, in minutes, to allow
            in search results. Must be greater than 0.

            Defaults to None, which shows flights of all lengths.

    Raises:
        ValueError: One or more parameters are not correctly formatted.
    """
    
    """
    config = _parse_config_file(config_file)
    flights = []
    for dep_city in config["DEPARTURE_PORT"]:
        for arr_city in config["ARRIVAL_PORT"]:
            # TODO: Allow date flexibility by vary by days
            dep_date = config["DEPARTURE_DATE"]
            trip_length = config["TRIP_LENGTH"]
            # TODO: Join this together
            flights.append(search_flights(dep_city, arr_port, dep_date, trip_length,
                config["MAX_COST"], config["MAX_DURATION"])


    query = build_query(dep_port, arr_port, dep_date, trip_length, max_cost)
    # TODO: Before printing flights, combine all flight data from multiple queries
    formatted = print_flights(_parse_flights(raw_result), max_duration)
    send_email(create_email(formatted, recipient), recipient)



def send_request(query):
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
    url = base_url + _get_auth_key()
    request = urllib2.Request(url, query, 
            {'Content-Type': 'application/json', 'Content-Length': len(query)})
    flight = urllib2.urlopen(request)
    response = flight.read()
    flight.close()
    return response

Flight = namedtuple('Flight', 'price legs')
Leg = namedtuple('Leg',
    'origin destination dep_time arr_time carrier flight_no duration')

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
        price = flight[u'saleTotal'][3:] # Crop off 'USD'
        legs = []
        for flight_slice in flight[u'slice']:
            duration = flight_slice[u'duration']
            for leg in flight_slice[u'segment']:
                carrier = leg[u'flight'][u'carrier']
                flight_no = leg[u'flight'][u'number']
                leg_data = leg[u'leg'][0]
                dep_time = leg_data[u'departureTime']
                arr_time = leg_data[u'arrivalTime']
                origin = leg_data[u'origin']
                arr_port = leg_data[u'destination']
                legs.append(Leg(origin, arr_port, dep_time, arr_time, carrier,
                    flight_no, duration))
        # Omit flights with airport transfers
        if _has_airport_transfer(legs):
            continue
        flights.append(Flight(price, legs))
    return sorted(flights, key=lambda x: float(x.price))

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
        # Time[5:10] gets Month-Day with year and timezone omitted 
        d_date = flight.legs[0].dep_time[5:10]
        # Note: Return date is based on return arrival time,
        #       not departure from destination time, so may not match
        #       flight dates.
        r_date = flight.legs[-1].arr_time[5:10]
        output += "Price: {}\t{} to {}\n".format(flight.price, d_date, r_date)
        for i in xrange(len(flight.legs)):
            output += "\tLeg {}:\n".format(i + 1)
            leg = flight.legs[i]
            output += "\t\tNumber: {}{}".format(leg.carrier, leg.flight_no)
            duration = "{} hr {} min".format(*divmod(int(leg.duration), 60))
            output += "\tTotal duration: {}\n".format(duration)
            output += "\t\tDeparture: {} at {}\t Arrival: {} at {}".format(
                 leg.origin, leg.dep_time, leg.destination, leg.arr_time)
            output += "\n\n"
        output += ("*" * 90) + "\n"
    return output

def _get_auth_key(path="DEFAULT"):
    """Fetches an authorization key stored elsewhere on the file system.

    This key is used for communicating with the QPX server, and is stored
    separately from the code for security reasons.

    Args:
        path: string, the full pathname (including filename) of the file
            containing the authorization key.

    Returns:
        string, the authorization key for the QPX server.
    """
    DEFAULT = "/Users/Toz/code/auth_key.txt"
    loc = DEFAULT if path == "DEFAULT" else path
    key = ""
    with open(loc, 'r') as input_file:
        key = input_file.read().strip()
    return key

# TODO: Should this be public facing or should everything go through
# search_flights?
def build_query(dep_port="CHI", arr_port="TYO", dep_date="2017-04-01", 
        trip_length=90, max_cost=900):
    """Builds a JSON query for checking flights on QPX.
    """
    # Error checking
    for code in dep_port, arr_port:
        if len(code) != 3:
            raise ValueError("Invalid city or airport code: {}".format(code))
    date = datetime.date(*map(int, dep_date.split("-")))
    if date < datetime.date.today():
        raise ValueError("Departure date may not be in the past")
    if trip_length <= 0:
        raise ValueError("Trip length must be greater than 0")
    if max_cost <= 0:
        raise ValueError("Max cost must be greater than 0")
    # Line locations in the default JSON query
    DEP_LOCS = (4, 10)
    ARR_LOCS = (5, 9)
    DEP_DATE_LOC = (6,)
    RET_DATE_LOC = (11,)
    PRICE_LOC = (18,)
    with open("base_query.json", "r") as raw_file:
        query = raw_file.readlines()
    if dep_port != "CHI":
        _replace_text(query, DEP_LOCS, "CHI", dep_port)
    if arr_port != "TYO":
        _replace_text(query, ARR_LOCS, "TYO", arr_port)
    return_date = _calculate_date(dep_date, trip_length)
    if dep_date != "2017-04-01":
        _replace_text(query, DEP_DATE_LOC, "2017-04-01", dep_date)
    _replace_text(query, RET_DATE_LOC, "2017-06-30", return_date)
    if max_cost != 900:
        _replace_text(query, PRICE_LOC, "900", str(max_cost))
    return "".join(query)

def _replace_text(query, lines, old_text, new_text):
    """Replaces text in a query at the given lines."""
    for loc in lines:
        line = query[loc]
        suffix = line[line.find(old_text) + len(old_text):]
        query[loc] = line[:line.find(old_text)] + new_text + suffix
    return query

def _calculate_date(start_date, duration):
    """Calculates a return date given a start date and duration."""
    start_date = datetime.date(*map(int, start_date.split("-")))
    new_date = start_date + datetime.timedelta(duration)
    year = format(new_date.year, '04')
    month = format(new_date.month, '02')
    day = format(new_date.day, '02')
    return "-".join((year, month, day))

recipient = "happyjolteon@gmail.com"
#search_flights(recipient, trip_length=58)
