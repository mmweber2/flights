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
        org_line = json_query[DEP_LOCS[0]]
        ret_line = json_query[DEP_LOCS[1]]
        new_suffix = dep_port + "\",\\\n"
        json_query[DEP_LOCS[0]] = org_line[:org_line.find("ORD")] + new_suffix
        json_query[DEP_LOCS[1]] = ret_line[:ret_line.find("ORD")] + new_suffix
    # TODO:
        # Set destination / return from airports
        # Calculate return date
        # Set dates
        # Set max price

    return json_query


    

