# seanox_ai_npl/units/units.py

from typing import TypedDict, Union

import re

_UNIT_SYMBOLS_SI_CONFORM_PATTERN = r"(?:A|bar|Bq|C|cd|d|dam|F|g|H|Hz|J|K|l|lm|lx|m|mol|N|\u03A9|Pa|p|rad|s|S|sr|T|t|V|w|Wb)"
_UNIT_SYMBOLS_SI_NOT_CONFORM_PATTERN = r"(?:a|AE|atm|At\u00FC|bbl|ct|dB|dpt|dz|Dz|ft|gal|ha|h|hl|hp|in|kt|lj|ls|mi|min|oz.|oz.tr.|pc|Pf|PS|pt|rm|sq.ft.|sq.in.|sq.mile|sq.yd.|St|u|v|V|yd|Z|\u00B0|\u00B0C|\u2032|\u2033|\u03C1|\u03C9)"

_UNIT_SYMBOLS_SI_CONFORM_FOR_EXPONENTS_PATTERN = r"(?:A|C|dam|F|H|J|K|m|\u03A9|s|T|V)"
_UNIT_SYMBOLS_SI_NOT_CONFORM_FOR_EXPONENTS_PATTERN = r"(?:a|ft|ha|in|lj|mi|pc|rm|St|v|yd|\u03C9)"
_UNIT_SYMBOLS_SI_NOT_CONFORM_FOR_INFORMAL_PREFIX_PATTERN = r"(?:a|ft|ha|in|m|mi|pc|rm|yd|St)"
_UNIT_SYMBOLS_SI_NOT_CONFORM_FOR_INFORMAL_SUFFIX_PATTERN = r"(?:a|ft|ha|in|m|mi|pc|rm|St|v|V|yd|\u03C9)"

_UNIT_SI_PREFIX_PATTERN = r"(?:Q|R|Y|Z|E|P|T|G|M|k|h|da|d|c|m|\u00B5|n|p|f|a|z|y|r|q)"
_UNIT_SI_SUFFIX_PATTERN = r"(?:\u207B?[\u00B9\u00B2\u00B3])"
_UNIT_INFORMAL_PREFIX_PATTERN = r"(?:q|sq )"
_UNIT_INFORMAL_SUFFIX_PATTERN = r"(?:2|3)"

# _UNIT_SYMBOLS_SI_CONFORM_FOR_EXPONENTS_PATTERN may contain _UNIT_SI_PREFIX_PATTERN
# and _UNIT_SI_SUFFIX_PATTERN
_UNIT_SI_CONFORM_1 = rf"""
    {_UNIT_SI_PREFIX_PATTERN}?
    {_UNIT_SYMBOLS_SI_CONFORM_FOR_EXPONENTS_PATTERN}
    {_UNIT_SI_SUFFIX_PATTERN}?
"""

# UNIT_SYMBOLS_SI_CONFORM may contain UNIT_SI_PREFIX_PATTERN
_UNIT_SI_CONFORM_2 = rf"""
    {_UNIT_SI_PREFIX_PATTERN}?
    {_UNIT_SYMBOLS_SI_CONFORM_PATTERN}
"""

# UNIT_SYMBOLS_SI_CONFORM_PATTERN may occur alone
_UNIT_SI_CONFORM_3 = rf"""
    {_UNIT_SYMBOLS_SI_CONFORM_PATTERN}
"""

_UNIT_SI_CONFORM_PATTERN = rf"""
    (?:{_UNIT_SI_CONFORM_1}
    |{_UNIT_SI_CONFORM_2}
    |{_UNIT_SI_CONFORM_3})
"""

# _UNIT_SYMBOLS_SI_NOT_CONFORM_FOR_INFORMAL_SUFFIX_PATTERN may contain
# _UNIT_INFORMAL_PREFIX_PATTERN and _UNIT_INFORMAL_SUFFIX_PATTERN
_UNIT_SI_NOT_CONFORM_1 = rf"""
    {_UNIT_INFORMAL_PREFIX_PATTERN}?
    {_UNIT_SYMBOLS_SI_NOT_CONFORM_FOR_INFORMAL_SUFFIX_PATTERN}
    {_UNIT_INFORMAL_SUFFIX_PATTERN}?
"""

# _UNIT_SYMBOLS_SI_NOT_CONFORM_FOR_INFORMAL_PREFIX_PATTERN may contain
# _UNIT_INFORMAL_PREFIX_PATTERN
_UNIT_SI_NOT_CONFORM_2 = rf"""
    {_UNIT_INFORMAL_PREFIX_PATTERN}?
    {_UNIT_SYMBOLS_SI_NOT_CONFORM_FOR_INFORMAL_PREFIX_PATTERN}
"""

# _UNIT_SYMBOLS_SI_NOT_CONFORM_PATTERN must not use _UNIT_SI_PREFIX_PATTERN

# _UNIT_SYMBOLS_SI_NOT_CONFORM_FOR_EXPONENTS_PATTERN may contain
# _UNIT_SI_SUFFIX_PATTERN
_UNIT_SI_NOT_CONFORM_3 = rf"""
    {_UNIT_SYMBOLS_SI_NOT_CONFORM_FOR_EXPONENTS_PATTERN}?
    {_UNIT_SI_SUFFIX_PATTERN}
"""

# _UNIT_SYMBOLS_SI_NOT_CONFORM_PATTERN may occur alone
_UNIT_SI_NOT_CONFORM_4 = rf"""
    {_UNIT_SYMBOLS_SI_NOT_CONFORM_PATTERN}
"""

_UNIT_SI_NOT_CONFORM_PATTERN = rf"""
    (?:{_UNIT_SI_NOT_CONFORM_1}
        |{_UNIT_SI_NOT_CONFORM_2}
        |{_UNIT_SI_NOT_CONFORM_3}
        |{_UNIT_SI_NOT_CONFORM_4})
"""

_UNIT_VARIANT_PATTERN = rf"""
    (?:{_UNIT_SI_CONFORM_PATTERN}
        |{_UNIT_SI_NOT_CONFORM_PATTERN})
"""


def _re_compile(expression: str) -> re.Pattern:
    return re.compile(
        re.sub(
            r"\s{2,}|[\r\n]+",
            "",
            expression)
    )


_UNIT_MATHEMATICAL_OPERATORS_PATTERN = r"[\u00B7\u002F]"
_UNIT_LOOK_AHEAD_PATTERN = r"(?:(?<=[\W\d])|^)"
_UNIT_LOOK_AHEAD_WITHOUT_SPACE_PATTERN = r"(?<=\d)"
_UNIT_LOOK_BEHIND_PATTERN = r"(?:(?=[^\w\u00B7\u002F])|$)"
_UNIT_MULTIPLE_SPACES = r"(?:\s{2,})"

UNIT_PATTERN = _re_compile(rf"""
    {_UNIT_LOOK_AHEAD_PATTERN}
    ({_UNIT_VARIANT_PATTERN}
        (?:{_UNIT_MATHEMATICAL_OPERATORS_PATTERN}
            {_UNIT_VARIANT_PATTERN})*)
    {_UNIT_LOOK_BEHIND_PATTERN}
""")

_UNIT_WITHOUT_SPACE_PATTERN = _re_compile(rf"""
    {_UNIT_LOOK_AHEAD_WITHOUT_SPACE_PATTERN}
    {_UNIT_VARIANT_PATTERN}
    (?:{_UNIT_MATHEMATICAL_OPERATORS_PATTERN}
        {_UNIT_VARIANT_PATTERN})*
    {_UNIT_LOOK_BEHIND_PATTERN}
""")

_UNIT_WITH_MULTIPLE_SPACES_PATTERN = _re_compile(rf"""
    {_UNIT_LOOK_AHEAD_PATTERN}
    ({_UNIT_MULTIPLE_SPACES})
    ({_UNIT_VARIANT_PATTERN}
        (?:{_UNIT_MATHEMATICAL_OPERATORS_PATTERN}
            {_UNIT_VARIANT_PATTERN})*)
    {_UNIT_LOOK_BEHIND_PATTERN}
""")

_UNIT_INFORMAL_PREFIX_PART_PATTERN = _re_compile(rf"""
    (?:^|{_UNIT_MATHEMATICAL_OPERATORS_PATTERN})
    {_UNIT_INFORMAL_PREFIX_PATTERN}
""")

_UNIT_INFORMAL_SUFFIX_PART_PATTERN = _re_compile(rf"""
    {_UNIT_INFORMAL_SUFFIX_PATTERN}
    (?:{_UNIT_MATHEMATICAL_OPERATORS_PATTERN}|$)
""")

_NUMERIC_LOOK_AHEAD_PATTERN = r"(?:(?<![\u00B1+\-,.\u2019\w\d])|^)"
_NUMERIC_SIGN_PATTERN = r"[\u00B1+\-]"
_NUMERIC_DE_PATTERN = r"(?:(?:(?:\d{1,3}(?:\.\d{3})*)|\d+)(?:,\d+)?)"
_NUMERIC_EN_PATTERN = r"(?:(?:(?:\d{1,3}(?:,\d{3})*)|\d+)(?:\.\d+))?"
_NUMERIC_CH_PATTERN = r"(?:(?:(?:\d{1,3}(?:\u2019\d{3})*)|\d+)(?:,\d+)?)"

NUMERIC_UNIT_PATTERN = _re_compile(rf"""
    {_NUMERIC_LOOK_AHEAD_PATTERN} 
    ({_NUMERIC_SIGN_PATTERN})?
    ({_NUMERIC_DE_PATTERN}|{_NUMERIC_EN_PATTERN}|{_NUMERIC_CH_PATTERN})
    (?:\s*)
    ({_UNIT_VARIANT_PATTERN}
        (?:{_UNIT_MATHEMATICAL_OPERATORS_PATTERN}
            {_UNIT_VARIANT_PATTERN})*)
    {_UNIT_LOOK_BEHIND_PATTERN}
""")

_NUMERIC_LEADING_ZEROS_ANTI_PATTERN = _re_compile(rf"^0\d")
_NUMERIC_INVALID_DECIMAL_THOUSAND_SEPARATOR_ANTI_PATTERN = _re_compile(rf"""
   (\d+\.\d+,\d+\.)
   |(\d+,\d+\.\d+,)
   |(\d+\u2019\d+,?\d+\u2019)
""")


class UnitValue(TypedDict):
    label: str
    start: int
    end: int
    text: str
    value: str
    unit: str
    normalized: str
    conform: bool
    informal: bool


class Unit(TypedDict):
    label: str
    start: int
    end: int
    text: str
    unit: str
    normalized: str
    conform: bool
    informal: bool


UnitEntry = Union[UnitValue, Unit]


def units(text: str) -> list[UnitEntry]:
    if not text:
        return []

    entities = []
    for match in NUMERIC_UNIT_PATTERN.finditer(text):
        sign, value, unit = match.groups()
        # Values with leading zeros before other numbers are invalid.
        if _NUMERIC_LEADING_ZEROS_ANTI_PATTERN.match(value):
            continue
        # Invalid decimal point/thousand separator combinations are not allowed
        if _NUMERIC_INVALID_DECIMAL_THOUSAND_SEPARATOR_ANTI_PATTERN.search(value):
            continue
        # Invalid thousand blocks are already ignored by the base expression

        # Units that appear more than once are not allowed
        subunits = re.split(_UNIT_MATHEMATICAL_OPERATORS_PATTERN, unit)
        if any(subunits.count(s) > 1 for s in set(subunits)):
            continue

        conform = False
        for sub in subunits:
            if not re.fullmatch(_UNIT_SYMBOLS_SI_CONFORM_PATTERN, sub):
                conform = False
                break
            else:
                conform = True

        informal = bool(
            _UNIT_INFORMAL_PREFIX_PART_PATTERN.search(unit)
            or _UNIT_INFORMAL_SUFFIX_PART_PATTERN.search(unit)
        )

        entity: UnitValue = {
            "label": "UNIT-VALUE",
            "start": match.start(),
            "end": match.end(),
            "text": match.group(),
            "value": f"{sign or ''}{value}",
            "unit": unit,
            "normalized": normalize(match.group().strip()),
            "conform": conform,
            "informal": informal
        }
        entities.append(entity)

        entity: Unit = {
            "label": "UNIT",
            "start": match.start(3),
            "end": match.end(3),
            "text": match.group(3),
            "unit": unit,
            "normalized": normalize(match.group(3).strip()),
            "conform": conform,
            "informal": informal
        }
        entities.append(entity)

    return entities


def normalize(text: str) -> str:
    text = _UNIT_WITHOUT_SPACE_PATTERN.sub(
        lambda match: " " + match.group(0),
        text
    )
    text = _UNIT_WITH_MULTIPLE_SPACES_PATTERN.sub(
        lambda match: " " + match.group(2),
        text
    )
    return text
