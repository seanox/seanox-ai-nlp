# tests/test_units.py

from seanox_ai_nlp.units import SpacingMode, spacing, units

import pytest
import re

def _parse_test_cases(data):
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

_TEST_CASES_01 = """
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
xxx 100,  m          -> xxx 100,  m
xxx 100,km           -> xxx 100,km
xxx 100, km          -> xxx 100, km
xxx 100,  km         -> xxx 100,  km
xxx 100,km/s         -> xxx 100,km/s
xxx 100, km/s        -> xxx 100, km/s
xxx 100,  km/s       -> xxx 100,  km/s

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
xxx 100.  m          -> xxx 100.  m
xxx 100.km           -> xxx 100.km
xxx 100. km          -> xxx 100. km
xxx 100.  km         -> xxx 100.  km
xxx 100.km/s         -> xxx 100.km/s
xxx 100. km/s        -> xxx 100. km/s
xxx 100.  km/s       -> xxx 100.  km/s

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

xxx 100.0  Ah/s      -> xxx 100.0 Ah/s
xxx 100.0  hW/s      -> xxx 100.0 hW/s
"""



@pytest.mark.parametrize("input,expected", _parse_test_cases(_TEST_CASES_01))
def test_normalize_01_a(input, expected):
    assert spacing(input) == expected

@pytest.mark.parametrize("input,expected", _parse_test_cases(_TEST_CASES_01))
def test_normalize_01_b(input, expected):
    assert spacing(input, SpacingMode.NUMERIC) == expected

_TEST_CASES_02 = """
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
xxx  km/s            -> xxx km/s

# simple units with commas in values
xxx 100,m            -> xxx 100,m
xxx 100, m           -> xxx 100, m
xxx 100,  m          -> xxx 100,  m
xxx 100,km           -> xxx 100,km
xxx 100, km          -> xxx 100, km
xxx 100,  km         -> xxx 100,  km
xxx 100,km/s         -> xxx 100,km/s
xxx 100, km/s        -> xxx 100, km/s
xxx 100,  km/s       -> xxx 100,  km/s

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
xxx 100.  m          -> xxx 100.  m
xxx 100.km           -> xxx 100.km
xxx 100. km          -> xxx 100. km
xxx 100.  km         -> xxx 100.  km
xxx 100.km/s         -> xxx 100.km/s
xxx 100. km/s        -> xxx 100. km/s
xxx 100.  km/s       -> xxx 100.  km/s

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

xxx 100.0  Ah/s      -> xxx 100.0 Ah/s
xxx 100.0  hW/s      -> xxx 100.0 hW/s
"""

@pytest.mark.parametrize("input,expected", _parse_test_cases(_TEST_CASES_02))
def test_normalize_02(input, expected):
    assert spacing(input, SpacingMode.ALPHANUMERIC) == expected

_TEST_CASES_03 = """
Die Batterie hält ca. 10h bei −20.5 °C.
Das Solarpanel produziert etwa 1.2 × 10^3W unter optimalen Bedingungen.
Mit einem Gewicht von ~2.3 kg ist das Gerät leicht tragbar.
Der Reifendruck liegt bei 2500hPa, empfohlen sind aber nur 2.5 bar.
Die Entfernung zum nächsten Ladepunkt beträgt rund 18 km, bei einer Durchschnittsgeschwindigkeit von 50km/h.
Einige Nutzer berichten sogar von 21.5kWh Verbrauch auf 100km.

Die Verpackung hat Maße von 35×22×12 cm und ein Volumen von ca. 9.24 l.
Das Display misst 15.6 " bei einer Auflösung von 1920×1080 px.
Der Lüfter erzeugt 34dB Geräuschpegel unter Last.
Laut Hersteller beträgt die Akkulaufzeit 12–14 h je nach Nutzung.
Das Gerät arbeitet in einem Temperaturbereich zwischen −10 °C und +45 °C.
Der Stromverbrauch liegt bei max. 65 W, die Ladezeit bei 3.5h über ein Netzteil mit 20V und 3.25A.
Die GPS-Genauigkeit beträgt etwa ±5 m.
Bei Windstärken über 60 km/h sollte das Gerät gesichert werden.

Das Plato befand sich auf 550 m Höhe bei einem relativen Luftdruck von 960hPa.
Die Signalreichweite lag bei bis zu 120 m auf freier Fläche.
Nach dem Update verbesserte sich die Bootzeit um 2.3 s, und die durchschnittliche CPU-Temperatur sank auf 36.5 °C.
Die Ladegeschwindigkeit wurde mit 0.8C angegeben.
Der Preis liegt aktuell bei etwa 299.99 €.
"""
@pytest.mark.parametrize("input", [_TEST_CASES_03])
def test_units_02(input):
    entities = units(input)
    print(entities)
#   assert TODO:
