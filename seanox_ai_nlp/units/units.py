# seanox_ai_npl/units/units.py

from typing import TypedDict, Union
from enum import Enum

import re

def _re_compile(expression: str, debug: bool=False) -> re.Pattern:
    expression = re.sub(r"\s{2,}|[\r\n]+", "", expression)
    if not debug:
        return re.compile(expression)
    return expression

_UNIT_SI_SYMBOLS_BASE_PATTERN = r"(?:A|cd|g|K|m|mol|s)"
_UNIT_SI_SYMBOLS_DERIVATION_PATTERN = r"(?:Bq|C|F|Gy|H|Hz|J|kat|lm|lx|N|\u00B0C|Pa|rad|S|sr|Sv|T|V|W|Wb|\u03A9)"
_UNIT_SI_SYMBOLS_EXTENSION_PATTERN = r"(?:a|AE|Ah|AU|b|B|bar|ct|d|Da|dB|db\([ACGZ]\)|dpt|eV|h|ha|kn|kt|l|L|mel|min|Np|oz\. tr\.|PS|pt|sone|tex|VA|Wh)"
_UNIT_SI_SYMBOLS_RELEVANT_PATTERN = r"(?:A|a|AE|Ah|AU|b|B|bar|Bq|C|cd|ct|d|Da|dB|db\([ACGZ]\)|dpt|eV|F|g|Gy|H|h|ha|Hz|J|K|kat|kn|kt|l|L|lm|lx|m|mel|min|mol|N|Np|\u00B0C|oz\. tr\.|Pa|PS|pt|rad|s|S|sone|sr|Sv|T|tex|V|VA|W|Wb|Wh|\u03A9)"
_UNIT_SI_SYMBOLS_PREFIX_PATTERN = r"(?:A|AE|AU|b|Bq|C|cd|ct|Da|eV|F|g|Gy|H|h|Hz|J|K|kat|l|L|lm|lx|m|mol|N|oz\. tr\.|Pa|rad|s|S|sr|Sv|t|T|V|VA|W|Wb|Wh|\u03A9)"
_UNIT_SI_SYMBOLS_SUFFIX_PATTERN = r"(?:A|Bq|C|F|g|H|J|kat|l|L|lm|lx|m|mol|Pa|s|S|sr|T|V|W|Wb|\u03A9)"
_UNIT_SI_SYMBOLS_PREFIX_SUFFIX_PATTERN = r"(?:A|Bq|C|F|g|H|J|kat|l|L|lm|lx|m|mol|Pa|s|S|sr|T|V|W|Wb|\u03A9)"
_UNIT_COMMON_SYMBOLS_PATTERN = r"(?:\''|%|\u2033|a|a|a|Ah|atm|At\u00FC|B|bar|bbl|d|dam|dB|db\([ACGZ]\)|dpt|dz|dz|ft|gal|ha|hp|in|kn|kt|kt|lb|lj|ls|mel|mi|min|Np|\u00B0|\u00B0C|oz|oz.|p|pc|PS|pt|rm|sone|St|tex|u|v|Var|yd|Z|\u03C1|\u03C9)"
_UNIT_INFORMAL_SYMBOLS_PATTERN = r"(?:ft|in|m|mi|mile|yd)"

_UNIT_SI_PREFIX_PATTERN = r"(?:Q|R|Y|Z|E|P|T|G|M|k|h|da|d|c|m|\u00B5|n|p|f|a|z|y|r|q)"
_UNIT_SI_SUFFIX_PATTERN = r"(?:\u207B?[\u00B9\u00B2\u00B3])"
_UNIT_SI_SYMBOLS_RELEVANT_SET = set(_UNIT_SI_SYMBOLS_RELEVANT_PATTERN[3:-1].split("|"))

_UNIT_INFORMAL_SYMBOLS_SET = set(_UNIT_INFORMAL_SYMBOLS_PATTERN[3:-1].split("|"))
_UNIT_INFORMAL_SI_SYMBOLS_SET = _UNIT_INFORMAL_SYMBOLS_SET & _UNIT_SI_SYMBOLS_RELEVANT_SET
_UNIT_INFORMAL_SI_SYMBOLS_PATTERN = rf"(?:{"|".join(_UNIT_INFORMAL_SI_SYMBOLS_SET)})"
_UNIT_INFORMAL_COMMON_SYMBOLS_SET = _UNIT_INFORMAL_SYMBOLS_SET - _UNIT_SI_SYMBOLS_RELEVANT_SET
_UNIT_INFORMAL_COMMON_SYMBOLS_PATTERN = rf"(?:{"|".join(_UNIT_INFORMAL_COMMON_SYMBOLS_SET)})"
_UNIT_INFORMAL_PREFIX_PATTERN = r"(?:c|q|sq\.\s?)"
_UNIT_INFORMAL_SUFFIX_PATTERN = r"(?:2|3)"

_UNIT_INFORMAL_SI_RAW_PATTERN = rf"""
    (?:
      {_UNIT_INFORMAL_PREFIX_PATTERN}?
      {_UNIT_SI_PREFIX_PATTERN}?
      {_UNIT_INFORMAL_SI_SYMBOLS_PATTERN}
      (?:
        {_UNIT_INFORMAL_SUFFIX_PATTERN}
        |{_UNIT_SI_SUFFIX_PATTERN} 
      )?
    )
"""

_UNIT_INFORMAL_COMMON_RAW_PATTERN = rf"""
    (?:
      {_UNIT_INFORMAL_PREFIX_PATTERN}?
      {_UNIT_INFORMAL_COMMON_SYMBOLS_PATTERN}
      {_UNIT_INFORMAL_SUFFIX_PATTERN}?
    )
"""

_UNIT_INFORMAL_RAW_PATTERN = rf"""
    (?:
      {_UNIT_INFORMAL_SI_RAW_PATTERN}
      |{_UNIT_INFORMAL_COMMON_RAW_PATTERN}
    )
"""

_UNIT_MATHEMATICAL_OPERATORS_PATTERN = r"[\u00B7\u00D7\u002A\u0078\u002F]"

_UNIT_LOOK_AHEAD_PATTERN = r"(?:(?<=[\W\d])|^)"
_UNIT_LOOK_AHEAD_WITHOUT_SPACE_PATTERN = r"(?<=\d)"
_UNIT_LOOK_BEHIND_PATTERN = r"(?:(?=[^\w\u00B7\u002F])|$)"
_UNIT_MULTIPLE_SPACES = r"(?:\s{2,})"

_NUMERIC_LOOK_AHEAD_PATTERN = r"(?:(?<![\u00B1+\-,\.\u2019\w\d])|^)"
_NUMERIC_SIGN_PATTERN = r"[\u00B1+\-~]"
_NUMERIC_DE_PATTERN = r"(?:(?:(?:\d{1,3}(?:\.\d{3})*)|\d+)(?:,\d+)?)"
_NUMERIC_EN_PATTERN = r"(?:(?:(?:\d{1,3}(?:,\d{3})*)|\d+)(?:\.\d+)?)"
_NUMERIC_CH_PATTERN = r"(?:(?:(?:\d{1,3}(?:\u2019\d{3})*)|\d+)(?:,\d+)?)"
_NUMERIC_SYMBOLIC_SEPARATOR = r"(?:[\u002B\u2212\u00B1\u002A\u00D7\u0078\u00B7\u003A\u00F7\u002F\u005E\u2013])"

_UNIT_SI_RAW_PATTERN = rf"""
    (?:{_UNIT_SI_PREFIX_PATTERN}?
    {_UNIT_SI_SYMBOLS_RELEVANT_PATTERN}
    {_UNIT_SI_SUFFIX_PATTERN}?)
"""

_UNIT_COMMON_RAW_PATTERN = rf"""
    (?:{_UNIT_COMMON_SYMBOLS_PATTERN})
"""

_UNIT_RAW_PATTERN = rf"""
    (?:
      {_UNIT_SI_RAW_PATTERN}
      |{_UNIT_INFORMAL_RAW_PATTERN}
      |{_UNIT_COMMON_RAW_PATTERN}
    )
"""

_UNIT_EXPRESSION_RAW_PATTERN = rf"""
    (?:
      {_UNIT_RAW_PATTERN}
      (?:
        {_UNIT_MATHEMATICAL_OPERATORS_PATTERN}
        {_UNIT_RAW_PATTERN}
      )*
    )
"""

NUMERIC_PATTERN = rf"""
    (?:
      {_NUMERIC_SIGN_PATTERN}?
      (?:
        {_NUMERIC_DE_PATTERN}
        |{_NUMERIC_EN_PATTERN}
        |{_NUMERIC_CH_PATTERN}
      )
      (?:
        \s*
        {_NUMERIC_SYMBOLIC_SEPARATOR}
        \s*
        (?:
          {_NUMERIC_DE_PATTERN}
          |{_NUMERIC_EN_PATTERN}
          |{_NUMERIC_CH_PATTERN}
        )
      )*
    )
"""

_UNIT_VALUE_PATTERN = rf"""
    {_NUMERIC_LOOK_AHEAD_PATTERN}
    (?P<unitValueNumeric>{NUMERIC_PATTERN})
    \s*
    (?P<unitValueUnit>{_UNIT_EXPRESSION_RAW_PATTERN})
    {_UNIT_LOOK_BEHIND_PATTERN}
"""

_UNIT_PATTERN = rf"""
    {_UNIT_LOOK_AHEAD_PATTERN}
    (?P<unitUnit>{_UNIT_EXPRESSION_RAW_PATTERN})
    {_UNIT_LOOK_BEHIND_PATTERN}
"""

UNIT_PATTERN = _re_compile(rf"""
    {_UNIT_VALUE_PATTERN}
    |{_UNIT_PATTERN}
""")

_UNIT_WITH_INVALID_SPACES_NUMERIC_PATTERN = _re_compile(rf"""
    (?<=\d)(\s{{2,}})?
    {_UNIT_EXPRESSION_RAW_PATTERN}
    {_UNIT_LOOK_BEHIND_PATTERN}
""")

_UNIT_WITH_INVALID_SPACES_ALPHANUMERIC_PATTERN = _re_compile(rf"""
    (?:
      (?:
        (?<=\d)(\s{{2,}})?)
        |(?:(?<=\w)(\s{{2,}})
      )
    )
    {_UNIT_EXPRESSION_RAW_PATTERN}
    {_UNIT_LOOK_BEHIND_PATTERN}
""")

_UNIT_WITH_INVALID_SPACES_ALL_PATTERN = _re_compile(rf"""
    (?:
      (?:(?<=\d)(\s{{2,}})?{_UNIT_EXPRESSION_RAW_PATTERN})
      |(?:\s{{2,}}{_UNIT_EXPRESSION_RAW_PATTERN})
      |(?:(?<![\w/*]){_UNIT_EXPRESSION_RAW_PATTERN})
    )
    {_UNIT_LOOK_BEHIND_PATTERN}  
""")

_UNIT_SI_VALIDATION_PATTERN = rf"""
    (?:
      (?:
        {_UNIT_SI_PREFIX_PATTERN}
        {_UNIT_SI_SYMBOLS_PREFIX_SUFFIX_PATTERN}
        {_UNIT_SI_SUFFIX_PATTERN}
      )
      |
      (?:
        {_UNIT_SI_PREFIX_PATTERN}
        {_UNIT_SI_SYMBOLS_PREFIX_PATTERN}
      )
      |
      (?:
        {_UNIT_SI_SYMBOLS_SUFFIX_PATTERN}
        {_UNIT_SI_SUFFIX_PATTERN}
      )
      |{_UNIT_SI_SYMBOLS_RELEVANT_PATTERN}
    )  
"""

_UNIT_COMMON_VALIDATION_PATTERN = rf"""
    (?:{_UNIT_COMMON_SYMBOLS_PATTERN})
"""

_UNIT_INFORMAL_VALIDATION_PATTERN = rf"""
    (?:
      {_UNIT_INFORMAL_PREFIX_PATTERN}?
      {_UNIT_INFORMAL_SYMBOLS_PATTERN}
      {_UNIT_INFORMAL_SUFFIX_PATTERN}?    
    )
"""

print(_re_compile(_UNIT_SI_VALIDATION_PATTERN, True))
print(_re_compile(_UNIT_COMMON_VALIDATION_PATTERN, True))
print(_re_compile(_UNIT_INFORMAL_VALIDATION_PATTERN, True))

_UNIT_VALIDATION_PATTERN = rf"""
    (?:
      {_UNIT_SI_VALIDATION_PATTERN}
      |{_UNIT_COMMON_VALIDATION_PATTERN}
      |{_UNIT_INFORMAL_VALIDATION_PATTERN}
    )
"""

_UNIT_VALIDATION_EXPRESSION_PATTERN = _re_compile(rf"""
    ^(?:
      {_UNIT_VALIDATION_PATTERN}
      (?:
        {_UNIT_MATHEMATICAL_OPERATORS_PATTERN}
        {_UNIT_VALIDATION_PATTERN}
      )*
    )$
""")

class SpacingMode(Enum):
    NUMERIC = _UNIT_WITH_INVALID_SPACES_NUMERIC_PATTERN
    ALPHANUMERIC = _UNIT_WITH_INVALID_SPACES_ALPHANUMERIC_PATTERN
    ALL = _UNIT_WITH_INVALID_SPACES_ALL_PATTERN

def spacing(text: str, mode: SpacingMode=SpacingMode.NUMERIC) -> str:
    text = mode.value.sub(
        lambda match: " " + match.group(0).strip(),
        text
    )
    return text

class UnitValue(TypedDict):
    label: str
    start: int
    end: int
    text: str
    value: str
    unit: str
    normalized: str
    standard: bool
    informal: bool

class Unit(TypedDict):
    label: str
    start: int
    end: int
    text: str
    unit: str
    normalized: str
    standard: bool
    informal: bool

UnitEntry = Union[UnitValue, Unit]

def units(text: str) -> list[UnitEntry]:

    if not text:
        return []

    entities = []
    for match in UNIT_PATTERN.finditer(text):
        groups = match.groupdict()
        numeric = groups.get("unitValueNumeric")
        unit = groups.get("unitValueUnit") or groups.get("unitUnit")

        if not (_UNIT_VALIDATION_EXPRESSION_PATTERN.match(unit)):
            continue

        if numeric:
            entity: UnitValue = {
                "label": "UNIT-VALUE",
                "start": match.start(),
                "end": match.end(),
                "text": match.group(),
                "value": numeric,
                "unit": unit,
            }
        else:
            entity: UnitValue = {
                "label": "UNIT",
                "start": match.start(),
                "end": match.end(),
                "text": match.group(),
                "unit": unit,
            }
        entities.append(entity)

    return entities
