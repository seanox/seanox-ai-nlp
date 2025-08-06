# tests/test_units_units.py

from seanox_ai_nlp.units import units
from typing import Optional, NamedTuple

import pytest


class Unit(NamedTuple):
    label: str
    start: int
    end: int
    text: str
    categories: tuple[str, ...]
    unit: str
    value: Optional[str] = None


@pytest.mark.parametrize("text", [(
    "Die Batterie h\u00e4lt ca. 10h bei \u221220.5 \u00b0C."
    "Das Solarpanel produziert etwa 1.2 \u00d7 10^3W unter optimalen Bedingungen."
    "Mit einem Gewicht von \u223c2.3 kg ist das Ger\u00e4t leicht tragbar."
    "Der Reifendruck liegt bei 2500hPa, empfohlen sind aber nur 2.5 bar."
    "Die Entfernung zum n\u00e4chsten Ladepunkt betr\u00e4gt rund 18 km, bei einer Durchschnittsgeschwindigkeit von 50km/h."
    "Einige Nutzer berichten sogar von 21.5kWh Verbrauch auf 100km."

    "Die Verpackung hat Ma\u00dfe von 35\u00d722\u00d712 cm und ein Volumen von ca. 9.24 l."
    "Das Display misst 15.6 \" bei einer Aufl\u00f6sung von 1920\u00d71080 px."
    "Der L\u00fcfter erzeugt 34dB Ger\u00e4uschpegel unter Last."
    "Laut Hersteller betr\u00e4gt die Akkulaufzeit 12\u201314 h je nach Nutzung."
    "Das Ger\u00e4t arbeitet in einem Temperaturbereich zwischen \u221210 \u00b0C und +45 \u00b0C."
    "Der Stromverbrauch liegt bei max. 65 W, die Ladezeit bei 3.5h \u00fcber ein Netzteil mit 20V und 3.25A."
    "Die GPS-Genauigkeit betr\u00e4gt etwa \u00b15 m."
    "Bei Windst\u00e4rken \u00fcber 60 km/h sollte das Ger\u00e4t gesichert werden."

    "Das Plato befand sich auf 550 m H\u00f6he bei einem relativen Luftdruck von 960hPa."
    "Die Signalreichweite lag bei bis zu 120 m auf freier Fl\u00e4che."
    "Nach dem Update verbesserte sich die Bootzeit um 2.3 s, und die durchschnittliche CPU-Temperatur sank auf 36.5 \u00b0C."
    "Die Ladegeschwindigkeit wurde mit 0.8C angegeben."
    "Der Preis liegt aktuell bei etwa 299.99 \u20ac."
)])
def test_units_01(text):
    expected_units = [
        Unit(label='UNIT-VALUE', start=22, end=25, text='10h', categories=('time',), unit='h', value='10'),
        Unit(label='UNIT', start=37, end=38, text='C', categories=('electricity',), unit='C', value=None),
        Unit(label='UNIT-VALUE', start=70, end=81, text='1.2 × 10^3W', categories=('power',), unit='W', value='1.2 × 10^3'),
        Unit(label='UNIT-VALUE', start=133, end=139, text='2.3 kg', categories=('mass',), unit='kg', value='2.3'),
        Unit(label='UNIT', start=144, end=147, text='das', categories=('time',), unit='das', value=None),
        Unit(label='UNIT-VALUE', start=195, end=202, text='2500hPa', categories=('pressure',), unit='hPa', value='2500'),
        Unit(label='UNIT-VALUE', start=228, end=235, text='2.5 bar', categories=('area radiation',), unit='bar', value='2.5'),
        Unit(label='UNIT-VALUE', start=287, end=292, text='18 km', categories=('length',), unit='km', value='18'),
        Unit(label='UNIT-VALUE', start=337, end=343, text='50km/h', categories=('length', 'time'), unit='km/h', value='50'),
        Unit(label='UNIT-VALUE', start=378, end=385, text='21.5kWh', categories=('power',), unit='kWh', value='21.5'),
        Unit(label='UNIT-VALUE', start=400, end=405, text='100km', categories=('length',), unit='km', value='100'),
        Unit(label='UNIT-VALUE', start=434, end=445, text='35×22×12 cm', categories=('length',), unit='cm', value='35×22×12'),
        Unit(label='UNIT-VALUE', start=470, end=476, text='9.24 l', categories=('volume',), unit='l', value='9.24'),
        Unit(label='UNIT-VALUE', start=558, end=562, text='34dB', categories=('time',), unit='dB', value='34'),
        Unit(label='UNIT-VALUE', start=629, end=636, text='12–14 h', categories=('time',), unit='h', value='12–14'),
        Unit(label='UNIT', start=672, end=674, text='in', categories=('length',), unit='in', value=None),
        Unit(label='UNIT', start=713, end=714, text='C', categories=('electricity',), unit='C', value=None),
        Unit(label='UNIT', start=724, end=725, text='C', categories=('electricity',), unit='C', value=None),
        Unit(label='UNIT-VALUE', start=760, end=764, text='65 W', categories=('power',), unit='W', value='65'),
        Unit(label='UNIT-VALUE', start=783, end=787, text='3.5h', categories=('time',), unit='h', value='3.5'),
        Unit(label='UNIT-VALUE', start=810, end=813, text='20V', categories=('electricity',), unit='V', value='20'),
        Unit(label='UNIT-VALUE', start=857, end=861, text='±5 m', categories=('length',), unit='m', value='±5'),
        Unit(label='UNIT-VALUE', start=883, end=890, text='60 km/h', categories=('length', 'time'), unit='km/h', value='60'),
        Unit(label='UNIT', start=898, end=901, text='das', categories=('time',), unit='das', value=None),
        Unit(label='UNIT-VALUE', start=951, end=956, text='550 m', categories=('length',), unit='m', value='550'),
        Unit(label='UNIT-VALUE', start=996, end=1002, text='960hPa', categories=('pressure',), unit='hPa', value='960'),
        Unit(label='UNIT-VALUE', start=1039, end=1044, text='120 m', categories=('length',), unit='m', value='120'),
        Unit(label='UNIT-VALUE', start=1112, end=1117, text='2.3 s', categories=('time',), unit='s', value='2.3'),
        Unit(label='UNIT', start=1175, end=1176, text='C', categories=('electricity',), unit='C', value=None),
        Unit(label='UNIT-VALUE', start=1211, end=1215, text='0.8C', categories=('electricity',), unit='C', value='0.8'),
    ]
    result_units = [
        Unit(
            label=entity.label,
            start=entity.start,
            end=entity.end,
            text=entity.text,
            categories=entity.categories,
            unit=entity.unit,
            value=entity.value
        )
        for entity in units(text)
    ]
    assert result_units == expected_units, f"\nExpected:\n{expected_units}\n\nGot:\n{result_units}"


@pytest.mark.parametrize("text", [(
    "The cruising speed of the Boeing 747 is approximately 900 km/h (559 mph)."
    "It is typically expressed in kilometers per hour (km/h) and miles per hour (mph)."
)])
def test_units_02(text):
    expected_units = [
        Unit(label='UNIT-VALUE', start=54, end=62, text='900 km/h', categories=('length', 'time'), unit='km/h', value='900'),
        Unit(label='UNIT-VALUE', start=64, end=71, text='559 mph', categories=('length',), unit='mph', value='559'),
        Unit(label='UNIT', start=99, end=101, text='in', categories=('length',), unit='in', value=None),
        Unit(label='UNIT', start=123, end=127, text='km/h', categories=('length', 'time'), unit='km/h', value=None),
        Unit(label='UNIT', start=149, end=152, text='mph', categories=('length',), unit='mph', value=None),
    ]
    result_units = [
        Unit(
            label=entity.label,
            start=entity.start,
            end=entity.end,
            text=entity.text,
            categories=entity.categories,
            unit=entity.unit,
            value=entity.value
        )
        for entity in units(text)
    ]
    assert result_units == expected_units, f"\nExpected:\n{expected_units}\n\nGot:\n{result_units}"
