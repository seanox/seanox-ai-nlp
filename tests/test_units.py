# tests/test_units.py

from seanox_ai_nlp.units import normalize, units

import pytest

__TEST_CASES_01 = [
    ("100m", "100 m"),
    ("100 m", "100 m"),
    ("100  m", "100 m"),
    ("100km", "100 km"),
    ("100 km", "100 km"),
    ("100  km", "100 km"),
    ("100km/s", "100 km/s"),
    ("100 km/s", "100 km/s"),
    ("100  km/s", "100 km/s"),

    ("x100m", "x100 m"),
    ("x100 m", "x100 m"),
    ("x100  m", "x100 m"),
    ("x100km", "x100 km"),
    ("x100 km", "x100 km"),
    ("x100  km", "x100 km"),
    ("x100km/s", "x100 km/s"),
    ("x100 km/s", "x100 km/s"),
    ("x100  km/s", "x100 km/s"),

    ("x100mx", "x100mx"),
    ("x100 mx", "x100 mx"),
    ("x100  mx", "x100  mx"),
    ("x100kmx", "x100kmx"),
    ("x100 kmx", "x100 kmx"),
    ("x100  kmx", "x100  kmx"),
    ("x100km/sx", "x100km/sx"),
    ("x100 km/sx", "x100 km/sx"),
    ("x100  km/sx", "x100  km/sx"),

    ("100m xxx", "100 m xxx"),
    ("100 m xxx", "100 m xxx"),
    ("100  m xxx", "100 m xxx"),
    ("100km xxx", "100 km xxx"),
    ("100 km xxx", "100 km xxx"),
    ("100  km xxx", "100 km xxx"),
    ("100km/s xxx", "100 km/s xxx"),
    ("100 km/s xxx", "100 km/s xxx"),
    ("100  km/s xxx", "100 km/s xxx"),

    ("xxx 100m xxx", "xxx 100 m xxx"),
    ("xxx 100 m xxx", "xxx 100 m xxx"),
    ("xxx 100  m xxx", "xxx 100 m xxx"),
    ("xxx 100km xxx", "xxx 100 km xxx"),
    ("xxx 100 km xxx", "xxx 100 km xxx"),
    ("xxx 100  km xxx", "xxx 100 km xxx"),
    ("xxx 100km/s xxx", "xxx 100 km/s xxx"),
    ("xxx 100 km/s xxx", "xxx 100 km/s xxx"),
    ("xxx 100  km/s xxx", "xxx 100 km/s xxx"),

    ("xxx 100m", "xxx 100 m"),
    ("xxx 100 m", "xxx 100 m"),
    ("xxx 100  m", "xxx 100 m"),
    ("xxx 100km", "xxx 100 km"),
    ("xxx 100 km", "xxx 100 km"),
    ("xxx 100  km", "xxx 100 km"),
    ("xxx 100km/s", "xxx 100 km/s"),
    ("xxx 100 km\u002Fs/ft", "xxx 100 km\u002Fs/ft"),
    ("xxx 100  km\u002Fs", "xxx 100 km\u002Fs"),

    ("xxx 100m", "xxx 100 m"),
    ("xxx 100 m", "xxx 100 m"),
    ("xxx 100  m", "xxx 100 m"),
    ("xxx 100km", "xxx 100 km"),
    ("xxx 100 km", "xxx 100 km"),
    ("xxx 100  km", "xxx 100 km"),

    ("xxxkm/s", "xxxkm/s"),
    ("xxx km/s", "xxx km/s"),
    ("xxx  km/s", "xxx  km/s"),

    ("xxx 100,m", "xxx 100,m"),
    ("xxx 100, m", "xxx 100, m"),
    ("xxx 100,  m", "xxx 100, m"),
    ("xxx 100,km", "xxx 100,km"),
    ("xxx 100, km", "xxx 100, km"),
    ("xxx 100,  km", "xxx 100, km"),
    ("xxx 100,km/s", "xxx 100,km/s"),
    ("xxx 100, km/s", "xxx 100, km/s"),
    ("xxx 100,  km/s", "xxx 100, km/s"),

    ("xxx 100,0m", "xxx 100,0 m"),
    ("xxx 100,0 m", "xxx 100,0 m"),
    ("xxx 100,0  m", "xxx 100,0 m"),
    ("xxx 100,0km", "xxx 100,0 km"),
    ("xxx 100,0 km", "xxx 100,0 km"),
    ("xxx 100,0  km", "xxx 100,0 km"),
    ("xxx 100,0km/s/ft", "xxx 100,0 km/s/ft"),
    ("xxx 100,0 km/s/qm", "xxx 100,0 km/s/qm"),
    ("xxx 100,0  km/s/m2", "xxx 100,0 km/s/m2"),

    ("xxx 100.m", "xxx 100.m"),
    ("xxx 100. m", "xxx 100. m"),
    ("xxx 100.  m", "xxx 100. m"),
    ("xxx 100.km", "xxx 100.km"),
    ("xxx 100. km", "xxx 100. km"),
    ("xxx 100.  km", "xxx 100. km"),
    ("xxx 100.km/s", "xxx 100.km/s"),
    ("xxx 100. km/s", "xxx 100. km/s"),
    ("xxx 100.  km/s", "xxx 100. km/s"),

    ("xxx 100.0m", "xxx 100.0 m"),
    ("xxx 100.0 m", "xxx 100.0 m"),
    ("xxx 100.0  m", "xxx 100.0 m"),
    ("xxx 100.0km", "xxx 100.0 km"),
    ("xxx 100.0 km", "xxx 100.0 km"),
    ("xxx 100.0  km", "xxx 100.0 km"),
    ("xxx 100.0km/s", "xxx 100.0 km/s"),
    ("xxx 100.0 km/s", "xxx 100.0 km/s"),
    ("xxx 100.0  km/s", "xxx 100.0 km/s")
]

@pytest.mark.parametrize("input,expected", __TEST_CASES_01)
def test_normalize(input, expected):
    assert normalize(input) == expected
