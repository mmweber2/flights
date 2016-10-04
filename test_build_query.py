from japan_flight_check import _build_query
from japan_flight_check import _calculate_date
from nose.tools import assert_equals

def test_build_unchanged():
    assert_equals(open("base_query.txt", "r").readlines(), _build_query())

def test_build_change_departure_city():
    result = _build_query(dep_port="IND")
    assert_equals(open("change_dep_city.txt", "r").readlines(), result)

def test_build_change_arrival_city():
    result = _build_query(arr_port="HND")
    assert_equals(open("change_arr_city.txt", "r").readlines(), result)

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




