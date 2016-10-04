import datetime
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
    return open(loc, 'r').read().strip()

def _build_query(dep_port="ORD", arr_port="NRT", dep_date="2017-04-01", 
        trip_length=90, max_cost=900):
    """Builds a JSON query for checking flights on QPX."""
    # TODO: Error checking and handling
    # Line locations in the default JSON query
    DEP_LOCS = (4, 10)
    ARR_LOCS = (5, 9)
    DEP_DATE_LOC = 6
    RET_DATE_LOC = 11
    PRICE_LOC = 22

    json_query = []
    with open("base_query.txt", "r") as raw_file:
        json_query = raw_file.readlines()
    if dep_port != "ORD":
        query = _replace_text(json_query, DEP_LOCS, "ORD", dep_port)
    if arr_port != "NRT":
        query = _replace_text(json_query, ARR_LOCS, "NRT", arr_port)
    # TODO:
        # Calculate return date
        # Set dates
        # Set max price
    return json_query

def _replace_text(query, lines, old_text, new_text):
    """Replaces text in a query at the given lines."""
    new_suffix = new_text + "\",\\\n"
    for loc in lines:
        line = query[loc]
        query[loc] = line[:line.find(old_text)] + new_suffix
    return query

def _calculate_date(start_date, duration):
    """Calculates a return date given a start date and duration."""
    start_date = datetime.date(*map(int, start_date.split("-")))
    new_date = start_date + datetime.timedelta(duration)
    year = format(new_date.year, '04')
    month = format(new_date.month, '02')
    day = format(new_date.day, '02')
    return "-".join((year, month, day))

