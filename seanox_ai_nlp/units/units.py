# seanox_ai_npl/units/units.py

# DESIGN NOTE
#
# This module relies entirely on statically aggregated and precompiled data
# structures derived from an external structured Excel source. The decision to
# embed unit definitions and classification patterns directly into the code is
# intentional and performance-driven.
#
# Rationale:
# - The unit data is curated and maintained externally in an Excel file.
# - At build time, the relevant entries are aggregated and transformed into
#   static regex-compatible strings and dictionaries.
# - This avoids runtime file I/O, dynamic parsing, or external dependencies.
# - All regex patterns are precompiled to maximize performance during text
#   processing.
#
# Trade-offs:
# - Flexibility is reduced: updates require regeneration of the static data.
# - Readability may be impacted due to the dense format of embedded strings.
# - However, this approach ensures high-speed recognition and classification of
#   units in NLP pipelines, especially when processing large volumes of text.
#
# Summary:
# This module prioritizes performance and reliability over dynamic flexibility.
# It is designed for production-grade NLP tasks where speed and consistency are
# critical.

from typing import Optional, NamedTuple
from enum import Enum
from functools import lru_cache

import re


def _re_compile(expression: str, debug: bool = False) -> re.Pattern:
    expression = re.sub(r"\s{2,}|[\r\n]+", "", expression)
    if not debug:
        return re.compile(expression)
    return expression


# Patterns generated from the Excel file
_UNIT_SI_SYMBOLS_BASE_PATTERN = r"(?:cd|g|K|m|mol|s)"
_UNIT_SI_SYMBOLS_DERIVATION_PATTERN = r"(?:Bq|C|F|Gy|H|Hz|J|kat|lm|lx|N|\u00BAC|Pa|rad|S|sr|Sv|T|V|W|Wb|\u03A9)"
_UNIT_SI_SYMBOLS_EXTENSION_PATTERN = r"(?:a|AE|Ah|AU|b|B|bar|ct|d|Da|dB|db\(A\)|db\(C\)|db\(G\)|db\(Z\)|dpt|eV|h|ha|kn|kt|l|L|mel|min|Np|oz\. tr\.|PS|pt|sone|tex|VA|Wh)"
_UNIT_SI_SYMBOLS_RELEVANT_PATTERN = r"(?:a|AE|Ah|AU|b|B|bar|Bq|C|cd|ct|d|Da|dB|db\(A\)|db\(C\)|db\(G\)|db\(Z\)|dpt|eV|F|g|Gy|H|h|ha|Hz|J|K|kat|kn|kt|l|L|lm|lx|m|mel|min|mol|N|Np|\u00BAC|oz\. tr\.|Pa|PS|pt|rad|s|S|sone|sr|Sv|T|tex|V|VA|W|Wb|Wh|\u03A9)"
_UNIT_SI_SYMBOLS_PREFIX_PATTERN = r"(?:AE|AU|b|Bq|C|cd|ct|Da|eV|F|g|Gy|H|h|Hz|J|K|kat|l|L|lm|lx|m|mol|N|oz\. tr\.|Pa|rad|s|S|sr|Sv|t|T|V|VA|W|Wb|Wh|\u03A9)"
_UNIT_SI_SYMBOLS_SUFFIX_PATTERN = r"(?:Bq|C|F|g|H|J|kat|l|L|lm|lx|m|mol|Pa|s|S|sr|T|V|W|Wb|\u03A9)"
_UNIT_SI_SYMBOLS_PREFIX_SUFFIX_PATTERN = r"(?:Bq|C|F|g|H|J|kat|l|L|lm|lx|m|mol|Pa|s|S|sr|T|V|W|Wb|\u03A9)"
_UNIT_COMMON_SYMBOLS_PATTERN = r"(?:\'|%|\u2033|a|Ah|atm|At\u00FC|B|bar|bbl|d|dam|dB|db\(A\)|db\(C\)|db\(G\)|db\(Z\)|dpt|dz|dz|ft|gal|ha|hp|in|kn|kt|kt|lb|lj|ls|mel|mi|min|Np|\u00BA|\u00BAC|oz|oz.|p|pc|PS|pt|rm|sone|St|tex|u|Var|yd|Z|\u03C9)"
_UNIT_INFORMAL_SYMBOLS_PATTERN = r"(?:ft|in|m|mi|mile|mph|yd)"

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

UNIT_OPERATORS_PATTERN = r"[\u00B7\u00D7\u002A\u0078\u002F]"

_UNIT_LOOK_AHEAD_PATTERN = r"(?:(?<=[\W\d])|^)"
_UNIT_LOOK_AHEAD_WITHOUT_SPACE_PATTERN = r"(?<=\d)"
_UNIT_LOOK_BEHIND_PATTERN = r"(?:(?=[^\w\u00B7\u002F])|$)"
_UNIT_MULTIPLE_SPACES = r"(?:\s{2,})"

_NUMERIC_LOOK_AHEAD_PATTERN = r"(?:(?<![\u00B1+\-,\.\u2019\w\d])|^)"
_NUMERIC_SIGN_PATTERN = r"[\u00B1+\-~]"
_NUMERIC_DE_PATTERN = r"(?:(?:(?:\d{1,3}(?:\.\d{3})*)|\d+)(?:,\d+)?)"
_NUMERIC_EN_PATTERN = r"(?:(?:(?:\d{1,3}(?:,\d{3})*)|\d+)(?:\.\d+)?)"
_NUMERIC_CH_PATTERN = r"(?:(?:(?:\d{1,3}(?:\u2019\d{3})*)|\d+)(?:,\d+)?)"
_NUMERIC_OPERATORS_PATTERN = r"(?:[\u002B\u2212\u00B1\u002A\u00D7\u0078\u00B7\u003A\u00F7\u002F\u005E\u2013])"

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
        {UNIT_OPERATORS_PATTERN}
        {_UNIT_RAW_PATTERN}
      )*
    )
"""

_NUMERIC_PATTERN = rf"""
    (?:
      {_NUMERIC_SIGN_PATTERN}?
      (?:
        {_NUMERIC_DE_PATTERN}
        |{_NUMERIC_EN_PATTERN}
        |{_NUMERIC_CH_PATTERN}
      )
      (?:
        \s*
        {_NUMERIC_OPERATORS_PATTERN}
        \s*
        (?:
          {_NUMERIC_DE_PATTERN}
          |{_NUMERIC_EN_PATTERN}
          |{_NUMERIC_CH_PATTERN}
        )
      )*
    )
"""

NUMERIC_PATTERN = _re_compile(_NUMERIC_PATTERN)
NUMERIC_OPERATORS_PATTERN = _re_compile(_NUMERIC_OPERATORS_PATTERN)

_UNIT_VALUE_PATTERN = rf"""
    {_NUMERIC_LOOK_AHEAD_PATTERN}
    (?P<unitValueNumeric>{_NUMERIC_PATTERN})
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
        {UNIT_OPERATORS_PATTERN}
        {_UNIT_VALIDATION_PATTERN}
      )*
    )$
""")

_UNIT_SI_CLASSIFICATION_PATTERN = rf"""
    (?:
      (?:
        (?P<unitSiPrefixSuffixPrefix>{_UNIT_SI_PREFIX_PATTERN})
        (?P<unitSiPrefixSuffixSymbol>{_UNIT_SI_SYMBOLS_PREFIX_SUFFIX_PATTERN})
        (?P<unitSiPrefixSuffixSuffix>{_UNIT_SI_SUFFIX_PATTERN})
      )
      |
      (?:
        (?P<unitSiPrefixPrefix>{_UNIT_SI_PREFIX_PATTERN})
        (?P<unitSiPrefixSymbol>{_UNIT_SI_SYMBOLS_PREFIX_PATTERN})
      )
      |
      (?:
        (?P<unitSiSuffixSymbol>{_UNIT_SI_SYMBOLS_SUFFIX_PATTERN})
        (?P<unitSiSuffixSuffix>{_UNIT_SI_SUFFIX_PATTERN})
      )
      |(?P<unitSiSymbol>{_UNIT_SI_SYMBOLS_RELEVANT_PATTERN})
    )  
"""

_UNIT_COMMON_CLASSIFICATION_PATTERN = rf"""
    (?P<unitCommonSymbol>{_UNIT_COMMON_SYMBOLS_PATTERN})
"""

_UNIT_INFORMAL_CLASSIFICATION_PATTERN = rf"""
    (?:
      (?P<unitInformalPrefix>{_UNIT_INFORMAL_PREFIX_PATTERN})?
      (?P<unitInformalSymbol>{_UNIT_INFORMAL_SYMBOLS_PATTERN})
      (?P<unitInformalSuffix>{_UNIT_INFORMAL_SUFFIX_PATTERN})?    
    )
"""

UNIT_CLASSIFICATION_PATTERN = _re_compile(rf"""
    (?:
      {_UNIT_SI_CLASSIFICATION_PATTERN}
      |{_UNIT_COMMON_CLASSIFICATION_PATTERN}
      |{_UNIT_INFORMAL_CLASSIFICATION_PATTERN}
    )
""")


def _dict_from_comma_separated_pairs(data: str) -> dict[str, str]:
    result = {}
    data = re.sub(r"\s*\|\s*[\r\n]\s*", "", data.strip())
    items = re.split(r"\s*\|\s*", data)
    for item in range(1, len(items) - 1, 2):
        key = items[item].strip()
        value = items[item + 1].strip()
        if key and value:
            result[key] = value
    return result


# For better maintainability and error analysis, a proprietary inline format
# that is not CSV is deliberately used, as it is only used internally and the
# format is fully controlled.
_UNIT_CLASSIFICATION_DICT = _dict_from_comma_separated_pairs(r"""
| \'       | length            | db\(C\) | acoustics                | L         | volume            | rad    | angle                   |
| \"       | length            | db\(G\) | acoustics                | lb        | mass              | rm     | volume                  |
| %        | ratio             | db\(Z\) | acoustics                | lj        | length astronomy  | s      | time                    |
| \u2032   | length            | dpt     | optics                   | lm        | light             | S      | electricity conductance |
| \u2033   | length            | dz      | quantity                 | ls        | light energy      | sone   | acoustics               |
| A        | electricity       | dz      | quantity                 | lx        | light             | sr     | angle                   |
| a        | area              | eV      | energy                   | m         | length            | St     | volume                  |
| AE       | astronomy length  | F       | electricity capacitance  | mel       | acoustics         | Sv     | radiation               |
| Ah       | electricity       | ft      | length                   | mi        | length            | t      | mass                    |
| atm      | pressure          | g       | mass                     | mile      | length            | T      | magnetic field          |
| At\u00FC | pressure          | gal     | volume                   | min       | time              | tex    | mass                    |
| AU       | astronomy length  | Gy      | radiation                | mol       | amount            | u      | mass atomic             |
| b        | area radiation    | H       | electricity              | mph       | length time       | V      | electricity             |
| B        | acoustics         | h       | time                     | N         | force             | VA     | electricity power       |
| bar      | pressure          | ha      | area                     | Np        | acoustics         | Var    | electricity power       |
| bbl      | volume            | hp      | power                    | \u00BA    | angle             | W      | power                   |
| Bq       | radiation         | Hz      | frequency                | \u00BAC   | temperature       | Wb     | magnetism               |
| C        | electricity       | in      | length                   | oz        | mass              | Wh     | energy                  |
| cd       | light             | J       | energy                   | oz.       | mass              | yd     | length                  |
| ct       | mass              | K       | temperature              | oz\. tr\. | mass              | Z      | mass                    |
| d        | time              | kat     | amount                   | p         | force             | \u03C9 | frequency rotation      |
| Da       | mass atomic       | kn      | speed                    | Pa        | pressure          | \u03A9 | electricity             |
| dam      | length            | kt      | mass                     | pc        | length astronomy  |        |                         |
| dB       | acoustics         | kt      | speed                    | PS        | power             |        |                         |
| db\(A\)  | acoustics         | l       | volume                   | pt        | volume            |        |                         |
""")


class SpacingMode(Enum):
    """
    Specifies patterns used to correct spacing between numeric/alphanumeric
    expressions and unit identifiers.

    Modes:
    - NUMERIC: Applies to spacing between numeric values and unit expressions.
    - ALPHANUMERIC: Applies to alphanumeric strings followed by unit expressions.
    - ALL: Applies broadly to numeric, alphanumeric, and special-character contexts.
    """
    NUMERIC = _UNIT_WITH_INVALID_SPACES_NUMERIC_PATTERN
    ALPHANUMERIC = _UNIT_WITH_INVALID_SPACES_ALPHANUMERIC_PATTERN
    ALL = _UNIT_WITH_INVALID_SPACES_ALL_PATTERN


def spacing(text: str, mode: SpacingMode = SpacingMode.NUMERIC) -> str:
    """
    Corrects invalid spacing between numbers and unit expressions.

    Args:
        text (str): Input string to be corrected
        mode (SpacingMode, optional): Correction mode for spacing.
            Default is SpacingMode.NUMERIC.

    Returns:
        str: Corrected text with corrected spacing
    """
    text = mode.value.sub(
        lambda match: " " + match.group(0).strip(),
        text
    )
    return text


class Unit(NamedTuple):
    """
    Represents a recognized unit entity extracted from text.

    Attributes:
        label (str): Classification label, e.g. 'UNIT-VALUE'.
        start (int): Start index of the unit in the original text.
        end (int): End index of the unit in the original text.
        text (str): Raw text fragment containing the unit.
        categories (tuple[str, ...]): Assigned semantic categories for the unit.
        unit (str): The extracted unit string (e.g. 'kg', 'm').
        value (Optional[str]): The numerical value associated with the unit, if present.
    """
    label: str
    start: int
    end: int
    text: str
    categories: tuple[str, ...]
    unit: str
    value: Optional[str] = None


@lru_cache(maxsize=256)
def _get_categories_for_unit(unit: str) -> tuple[str, ...]:
    categories = []
    for unitEntry in re.split(UNIT_OPERATORS_PATTERN, unit):
        match = UNIT_CLASSIFICATION_PATTERN.search(unitEntry)
        category = _UNIT_CLASSIFICATION_DICT.get(
            match.group("unitSiPrefixSuffixSymbol")
            or match.group("unitSiPrefixSymbol")
            or match.group("unitSiSuffixSymbol")
            or match.group("unitSiSymbol")
            or match.group("unitCommonSymbol")
            or match.group("unitInformalSymbol")
        )
        if category:
            categories.append(category)
    return tuple(categories)


def units(text: str) -> list[Unit]:
    """
    Extracts valid unit expressions and associated numeric values from a given text.

    Args:
        text (str): Input string to analyze.

    Returns:
        list[Unit]: List of Unit objects representing detected unit entities.

    Notes:
        - Only units matching known validation patterns will be returned.
        - Numeric expression preceding units will be included when available.
        - Designed for use in NLP pipelines, extraction, and preprocessing tasks.
    """

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
            entities.append(
                Unit(
                    label="UNIT-VALUE",
                    start=match.start(),
                    end=match.end(),
                    text=match.group(),
                    unit=unit,
                    value=numeric,
                    categories=_get_categories_for_unit(unit)
                )
            )
        else:
            entities.append(
                Unit(
                    label="UNIT-VALUE",
                    start=match.start(),
                    end=match.end(),
                    text=match.group(),
                    unit=unit,
                    categories=_get_categories_for_unit(unit)
                )
            )

    return entities
