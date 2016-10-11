from japan_flight_check import build_query
from japan_flight_check import _calculate_date
from japan_flight_check import send_request
from nose.tools import assert_equals

def test_build_unchanged():
    result = build_query()
    expected = "" 
    with open("base_query.json", "r") as input_file:
        expected = "".join(input_file.readlines())
    assert_equals(expected, result)

def test_build_change_departure_city():
    result = build_query(dep_port="IND")
    expected = "" 
    with open("change_dep_city.json", "r") as input_file:
        expected = "".join(input_file.readlines())
    assert_equals(expected, result)

def test_build_change_arrival_city():
    result = build_query(arr_port="KIX")
    expected = "" 
    with open("change_arr_city.json", "r") as input_file:
        expected = "".join(input_file.readlines())
    assert_equals(expected, result)

def test_calculate_date_unchanged():
    date = "2016-10-04"
    assert_equals(_calculate_date(date, 0), date)

def test_calculate_date_same_month():
    date = "2016-10-04"
    assert_equals(_calculate_date(date, 2), "2016-10-06")

def test_calculate_date_new_month_30():
    date = "2016-09-30"
    assert_equals(_calculate_date(date, 2), "2016-10-02")

def test_calculate_date_new_year():
    date = "2016-12-30"
    assert_equals(_calculate_date(date, 3), "2017-01-02")

def test_build_change_departure_date():
    result = build_query(dep_date="2017-05-01")
    expected = "" 
    with open("change_dep_date.json", "r") as input_file:
        expected = "".join(input_file.readlines())
    assert_equals(expected, result)

def test_build_change_max_cost():
    result = build_query(max_cost=2000)
    expected = "" 
    with open("change_max_cost.json", "r") as input_file:
        expected = "".join(input_file.readlines())
    assert_equals(expected, result)

def test_send_request():
    #send_request(build_query())
    pass
