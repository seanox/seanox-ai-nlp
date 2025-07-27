# tests/test_units.py

from seanox_ai_nlp.units import normalize, units

import pytest
import re

__TEST_CASES_01 = """
# simple units
100m                 -> 100 m
100 m                -> 100 m
100  m               -> 100 m
100km                -> 100 km
100 km               -> 100 km
100  km              -> 100 km
100km/s              -> 100 km/s
100 km/s             -> 100 km/s
100  km/s            -> 100 km/s

# simple units with invalid prefix
x100m                -> x100 m
x100 m               -> x100 m
x100  m              -> x100 m
x100km               -> x100 km
x100 km              -> x100 km
x100  km             -> x100 km
x100km/s             -> x100 km/s
x100 km/s            -> x100 km/s
x100  km/s           -> x100 km/s

# simple units with invalid suffix
x100mx               -> x100mx
x100 mx              -> x100 mx
x100  mx             -> x100  mx
x100kmx              -> x100kmx
x100 kmx             -> x100 kmx
x100  kmx            -> x100  kmx
x100km/sx            -> x100km/sx
x100 km/sx           -> x100 km/sx
x100  km/sx          -> x100  km/sx

# simple units with downstream text
100m xxx             -> 100 m xxx
100 m xxx            -> 100 m xxx
100  m xxx           -> 100 m xxx
100km xxx            -> 100 km xxx
100 km xxx           -> 100 km xxx
100  km xxx          -> 100 km xxx
100km/s xxx          -> 100 km/s xxx
100 km/s xxx         -> 100 km/s xxx
100  km/s xxx        -> 100 km/s xxx

# simple units embedded
xxx 100m xxx         -> xxx 100 m xxx
xxx 100 m xxx        -> xxx 100 m xxx
xxx 100  m xxx       -> xxx 100 m xxx
xxx 100km xxx        -> xxx 100 km xxx
xxx 100 km xxx       -> xxx 100 km xxx
xxx 100  km xxx      -> xxx 100 km xxx
xxx 100km/s xxx      -> xxx 100 km/s xxx
xxx 100 km/s xxx     -> xxx 100 km/s xxx
xxx 100  km/s xxx    -> xxx 100 km/s xxx
xxx 100 km\u00B7s/ft -> xxx 100 km\u00B7s/ft
xxx 100  km\u00B7s   -> xxx 100 km\u00B7s

# simple units with preceding text
xxx 100m             -> xxx 100 m
xxx 100 m            -> xxx 100 m
xxx 100  m           -> xxx 100 m
xxx 100km            -> xxx 100 km
xxx 100 km           -> xxx 100 km
xxx 100  km          -> xxx 100 km
xxx 100km/s          -> xxx 100 km/s
xxx 100 km/s/ft      -> xxx 100 km/s/ft
xxx 100  km/s        -> xxx 100 km/s

# simple units without values (invalid)
xxxkm/s              -> xxxkm/s
xxx km/s             -> xxx km/s
xxx  km/s            -> xxx  km/s

# simple units with commas in values
xxx 100,m            -> xxx 100,m
xxx 100, m           -> xxx 100, m
xxx 100,  m          -> xxx 100, m
xxx 100,km           -> xxx 100,km
xxx 100, km          -> xxx 100, km
xxx 100,  km         -> xxx 100, km
xxx 100,km/s         -> xxx 100,km/s
xxx 100, km/s        -> xxx 100, km/s
xxx 100,  km/s       -> xxx 100, km/s

# simple units with commas as decimals
xxx 100,0m           -> xxx 100,0 m
xxx 100,0 m          -> xxx 100,0 m
xxx 100,0  m         -> xxx 100,0 m
xxx 100,0km          -> xxx 100,0 km
xxx 100,0 km         -> xxx 100,0 km
xxx 100,0  km        -> xxx 100,0 km
xxx 100,0km/s/ft     -> xxx 100,0 km/s/ft
xxx 100,0 km/s/qm    -> xxx 100,0 km/s/qm
xxx 100,0  km/s/m2   -> xxx 100,0 km/s/m2

# simple units with decimal point but without decimal place
xxx 100.m            -> xxx 100.m
xxx 100. m           -> xxx 100. m
xxx 100.  m          -> xxx 100. m
xxx 100.km           -> xxx 100.km
xxx 100. km          -> xxx 100. km
xxx 100.  km         -> xxx 100. km
xxx 100.km/s         -> xxx 100.km/s
xxx 100. km/s        -> xxx 100. km/s
xxx 100.  km/s       -> xxx 100. km/s

# simple units with decimal point
xxx 100.0m           -> xxx 100.0 m
xxx 100.0 m          -> xxx 100.0 m
xxx 100.0  m         -> xxx 100.0 m
xxx 100.0km          -> xxx 100.0 km
xxx 100.0 km         -> xxx 100.0 km
xxx 100.0  km        -> xxx 100.0 km
xxx 100.0km/s        -> xxx 100.0 km/s
xxx 100.0 km/s       -> xxx 100.0 km/s
xxx 100.0  km/s      -> xxx 100.0 km/s
"""

def __parse_test_cases(data):
    cases = []
    for line in data.strip().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        match = re.split(r"\s*->\s*", line, maxsplit=1)
        if len(match) == 2:
            input, expected = match
            cases.append((input.strip(), expected.strip()))
    return cases

@pytest.mark.parametrize("input,expected", __parse_test_cases(__TEST_CASES_01))
def test_normalize(input, expected):
    assert normalize(input) == expected
