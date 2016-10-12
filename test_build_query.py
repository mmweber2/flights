from japan_flight_check import build_query
from japan_flight_check import _calculate_date
from japan_flight_check import _has_airport_transfer
from japan_flight_check import send_request
from japan_flight_check import Leg

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

def test_transfer_true():
    legs = [
        Leg(origin=u'ORD', destination=u'TPE',
        dep_time=u'2017-04-01T00:30-05:00', arr_time=u'2017-04-02T04:45+08:00',
        carrier=u'BR', flight_no=u'55', duration=1765), 
        Leg(origin=u'TSA', destination=u'HND',
        dep_time=u'2017-04-02T16:00+08:00', arr_time=u'2017-04-02T19:55+09:00',
        carrier=u'BR', flight_no=u'190', duration=1765)
    ]
    assert _has_airport_transfer(legs)

def test_transfer_false():
    legs = [
        Leg(origin=u'ORD', destination=u'NRT',
        dep_time=u'2017-04-01T00:30-05:00', arr_time=u'2017-04-02T04:45+08:00',
        carrier=u'BR', flight_no=u'55', duration=1765), 
        Leg(origin=u'NRT', destination=u'HND',
        dep_time=u'2017-04-02T16:00+08:00', arr_time=u'2017-04-02T19:55+09:00',
        carrier=u'BR', flight_no=u'190', duration=1765)
    ]
    assert not _has_airport_transfer(legs)
