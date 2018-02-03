from flight_check import _parse_flights
from nose.tools import assert_equals
from nose.tools import assert_raises

def test_parse_flights_non_USD():
    result = ""
    with open("./tests/response_test_non_USD.json", "r") as input_file:
        result = input_file.read()
    assert_raises(ValueError, _parse_flights, result)

# TODO: Get or make sample JSON data of a flight with a transfer
def test_parse_flights_airport_transfer():
    pass
    #result = ""
    #with open("./tests/response_test_transfer_airport.json", "r") as input_file:
    #    result = input_file.read()
    #assert_raises(ValueError, _parse_flights, result)