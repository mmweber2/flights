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
    # Line locations in the default JSON query
    DEP_LOCS = (4, 9)
    ARR_LOCS = (5, 10)
    DEP_DATE_LOC = 6
    RET_DATE_LOC = 11
    PRICE_LOC = 22

    json_query = []
    with open("base_query.txt", "r") as raw_file:
        json_query = raw_file.readlines()
    if dep_port != "ORD":
        new_dep = origin_line[:origin_line.find("ORD")] + dep_port + "\","
        for i in json_query[DEP_LOCS]:
            json_query[i] = new_dep

    # TODO:
        # Set destination / return from airports
        # Calculate return date
        # Set dates
        # Set max price

    return json_query


    

