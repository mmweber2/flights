from japan_flight_check import _build_query
from nose.tools import assert_equals

def test_build_unchanged():
    assert_equals(open("base_query.txt", "r").readlines(), _build_query())

def test_build_change_departure_city():
    result = _build_query(dep_port="IND")
    assert_equals(open("change_dep_city.txt", "r").readlines(), result)

def test_build_change_arrival_city():
    result = _build_query(arr_port="HND")
    assert_equals(open("change_arr_city.txt", "r").readlines(), result)



