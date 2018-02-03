import datetime
from time import strftime
import json
from flight_check import build_query
from flight_check import _calculate_date
from flight_check import _has_airport_transfer
from flight_check import _parse_flights
from flight_check import print_flights
from flight_check import send_request
from flight_check import Leg
from nose.tools import assert_equals
from nose.tools import assert_raises

def test_build_unchanged():
    result = build_query()
    base_query = None
    with open("base_query.json", "r") as input_file:
        base_query = json.load(input_file)
    # build_query returns a JSON dump formatted string
    assert_equals(json.dumps(base_query), result)

def test_build_change_departure_city():
    result = build_query(dep_port="IND")
    expected = None
    with open("change_dep_city.json", "r") as input_file:
        expected = json.load(input_file)
    assert_equals(json.dumps(expected), result)

def test_build_change_arrival_city():
    result = build_query(arr_port="KIX")
    expected = None
    with open("change_arr_city.json", "r") as input_file:
        expected = json.load(input_file)
    assert_equals(json.dumps(expected), result)

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
    expected = None
    with open("change_dep_date.json", "r") as input_file:
        expected = json.load(input_file)
    assert_equals(json.dumps(expected), result)

def test_build_change_departure_date_today():
    today = datetime.date.today().strftime("%Y-%m-%d")
    result = build_query(dep_date=today)
    # I don't see a way to match the result for a changing query
    # with an expected value without doing the same thing the main code does:
    # calculating the new return date, changing both of the dates in the JSON,
    # and returning.
    # I'll just confirm that this doesn't raise a ValueError.
    assert result

def test_build_change_departure_date_to_past():
    assert_raises(ValueError, build_query, dep_date="2016-04-01")

def test_build_change_max_cost():
    result = build_query(max_cost=2000)
    expected = None
    with open("change_max_cost.json", "r") as input_file:
        expected = json.load(input_file)
    assert_equals(json.dumps(expected), result)

def test_build_change_max_cost_remove():
    result = build_query(max_cost=None)
    expected = None
    with open("remove_max_cost.json", "r") as input_file:
        expected = json.load(input_file)
    assert_equals(json.dumps(expected), result)

def test_build_change_max_cost_zero():
    assert_raises(ValueError, build_query, max_cost=0)

# Commented out to run other tests without sending queries
def test_send_request():
    #send_request(build_query())
    pass

def test_transfer_true():
    legs = [
        Leg(origin=u'ORD', destination=u'TPE',
        dep_time=u'2017-04-01T00:30-05:00', arr_time=u'2017-04-02T04:45+08:00',
        carrier=u'BR', flight_num=u'55', duration=1765), 
        Leg(origin=u'TSA', destination=u'HND',
        dep_time=u'2017-04-02T16:00+08:00', arr_time=u'2017-04-02T19:55+09:00',
        carrier=u'BR', flight_num=u'190', duration=1765)
    ]
    assert _has_airport_transfer(legs)

def test_transfer_false():
    legs = [
        Leg(origin=u'ORD', destination=u'NRT',
        dep_time=u'2017-04-01T00:30-05:00', arr_time=u'2017-04-02T04:45+08:00',
        carrier=u'BR', flight_num=u'55', duration=1765), 
        Leg(origin=u'NRT', destination=u'HND',
        dep_time=u'2017-04-02T16:00+08:00', arr_time=u'2017-04-02T19:55+09:00',
        carrier=u'BR', flight_num=u'190', duration=1765)
    ]
    assert not _has_airport_transfer(legs)

def test_change_max_duration_valid_with_results():
    result = ""
    with open("sample_result.txt", "r") as input_file:
        result = input_file.read()
    parsed = _parse_flights(result)
    # There should only be one flight in these results
    assert_equals(1, print_flights(parsed, 1400).count("Price"))

def test_change_max_duration_valid_no_results():
    result = ""
    with open("sample_result.txt", "r") as input_file:
        result = input_file.read()
    parsed = _parse_flights(result)
    # There should not be any flights in these results
    assert not print_flights(parsed, 1200)

def test_change_max_duration_zero():
    result = ""
    with open("sample_result.txt", "r") as input_file:
        result = input_file.read()
    parsed = _parse_flights(result)
    assert_raises(ValueError, print_flights, parsed, 0)

# TODO:
# Build query tests:
# Invalid city/airport codes (too short/long)
# Invalid city/airport codes (not real)
# Trip length = 0
#
# Add test for flight results not in USD
# Add test for query with no max price
# Add email sending/creating tests (use mock for sending)
