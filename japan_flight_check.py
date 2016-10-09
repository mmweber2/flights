import datetime
import urllib2

def send_request(query):
    """Sends a flight query to the QPX Server.

    Using a query string from build_query, sends an HTTP request to the QPX server
    and returns the response.

    Limited to 50 queries per day.

    Args:
        query: string, JSON-formatted data generated by build_query.

    Returns:
        A string containing the JSON-formatted data of the search results.
    """
    # TODO: Error checking of query
    base_url = "https://www.googleapis.com/qpxExpress/v1/trips/search?key="
    url = base_url + _get_auth_key()
    request = urllib2.Request(url, query, 
            {'Content-Type': 'application/json', 'Content-Length': len(query)})
    flight = urllib2.urlopen(request)
    response = flight.read()
    flight.close()
    return response

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

def build_query(dep_port="CHI", arr_port="TYO", dep_date="2017-04-01", 
        trip_length=90, max_cost=900):
    """Builds a JSON query for checking flights on QPX."""
    # TODO: Error checking and handling
    # Line locations in the default JSON query
    DEP_LOCS = (4, 10)
    ARR_LOCS = (5, 9)
    DEP_DATE_LOC = 6
    RET_DATE_LOC = 11
    PRICE_LOC = 22

    with open("base_query.json", "r") as raw_file:
        query = raw_file.readlines()
    if dep_port != "CHI":
        _replace_text(query, DEP_LOCS, "CHI", dep_port)
    if arr_port != "TYO":
        _replace_text(query, ARR_LOCS, "TYO", arr_port)
    return_date = _calculate_date(dep_date, trip_length)
    if dep_date != "2017-04-01":
        _replace_text(query, [DEP_DATE_LOC], "2017-04-01", dep_date)
    _replace_text(query, [RET_DATE_LOC], "2017-06-30", return_date)
    # TODO:
        # Set dates
        # Set max price
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
