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

# Arbitrary choices to use while testing other parts
base_query = ("CHI", "TYO", "2018-07-02", 80)

def test_build_queries_departure_date_in_past():
    # global base_query
    dep_port, arr_port, _, trip_length = base_query
    assert_raises(ValueError, build_query, dep_port, arr_port,
        "2016-04-01", trip_length)

def test_build_queries_set_max_cost():
    dep_port, arr_port, dep_date, trip_length = base_query
    result = build_query(dep_port, arr_port, dep_date, trip_length,
                         max_cost=2000)
    expected = None
    with open("./tests/change_max_cost.json", "r") as input_file:
        expected = json.load(input_file)
    assert_equals(json.dumps(expected), result)

def test_build_change_max_cost_zero():
    dep_port, arr_port, dep_date, trip_length = base_query
    assert_raises(ValueError, build_query, dep_port, arr_port,
                  dep_date, trip_length, max_cost=0)

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
    with open("./tests/sample_response.json", "r") as input_file:
        result = input_file.read()
    parsed = _parse_flights(result)
    # There should only be one flight in these results
    assert_equals(1, print_flights(parsed, 1400).count("Price"))

def test_change_max_duration_valid_no_results():
    result = ""
    with open("./tests/response_test_duration.json", "r") as input_file:
        result = input_file.read()
    parsed = _parse_flights(result)
    # There should not be any flights in these results
    print print_flights(parsed, 1200)
    assert not print_flights(parsed, 1200)

def test_change_max_duration_zero():
    result = ""
    with open("./tests/sample_response.json", "r") as input_file:
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
