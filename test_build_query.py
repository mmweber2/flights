from japan_flight_check import _build_query
from nose.tools import assert_equals

def test_build_unchanged():
    assert_equals(open("base_query.txt", "r").readlines(), _build_query())
