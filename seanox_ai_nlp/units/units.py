# seanox_ai_npl/units/units.py

import re

__UNIT_SYMBOLS_SI_CONFORM_PATTERN = r"(?:A|bar|Bq|C|cd|d|dam|F|g|H|Hz|J|K|l|lm|lx|m|mol|N|\u03A9|Pa|p|rad|s|S|sr|T|t|V|w|Wb)"
__UNIT_SYMBOLS_SI_NOT_CONFORM_PATTERN = r"(?:a|AE|atm|At\u00FC|bbl|ct|dB|dpt|dz|Dz|ft|gal|ha|h|hl|hp|in|kt|lj|ls|mi|min|oz.|oz.tr.|pc|Pf|PS|pt|rm|sq.ft.|sq.in.|sq.mile|sq.yd.|St|u|v|V|yd|Z|\u00B0|\u00B0C|\u2032|\u2033|\u03C1|\u03C9)"

__UNIT_SYMBOLS_SI_CONFORM_FOR_EXPONENTS_PATTERN = r"(?:A|C|dam|F|H|J|K|m|\u03A9|s|T|V)"
__UNIT_SYMBOLS_SI_NOT_CONFORM_FOR_EXPONENTS_PATTERN = r"(?:a|ft|ha|in|lj|mi|pc|rm|St|v|yd|\u03C9)"
__UNIT_SYMBOLS_SI_NOT_CONFORM_FOR_INFORMAL_PREFIX_PATTERN = r"(?:a|ft|ha|in|m|mi|pc|rm|yd|St)"
__UNIT_SYMBOLS_SI_NOT_CONFORM_FOR_INFORMAL_SUFFIX_PATTERN = r"(?:a|ft|ha|in|m|mi|pc|rm|St|v|V|yd|\u03C9)"

__UNIT_SI_PREFIX_PATTERN = r"(?:Q|R|Y|Z|E|P|T|G|M|k|h|da|d|c|m|\u00B5|n|p|f|a|z|y|r|q)"
__UNIT_SI_SUFFIX_PATTERN = r"(?:\u207B?[\u00B9\u00B2\u00B3])"
__UNIT_INFORMAL_PREFIX_PATTERN = r"(?:q|sq )"
__UNIT_INFORMAL_SUFFIX_PATTERN = r"(?:2|3)"

# __UNIT_SYMBOLS_SI_CONFORM_FOR_EXPONENTS_PATTERN may contain __UNIT_SI_PREFIX_PATTERN
# and __UNIT_SI_SUFFIX_PATTERN
__UNIT_SI_CONFORM_1 = rf"""
    {__UNIT_SI_PREFIX_PATTERN}?
    {__UNIT_SYMBOLS_SI_CONFORM_FOR_EXPONENTS_PATTERN}
    {__UNIT_SI_SUFFIX_PATTERN}?
"""

# UNIT_SYMBOLS_SI_CONFORM may contain UNIT_SI_PREFIX_PATTERN
__UNIT_SI_CONFORM_2 = rf"""
    {__UNIT_SI_PREFIX_PATTERN}?
    {__UNIT_SYMBOLS_SI_CONFORM_PATTERN}
"""

# UNIT_SYMBOLS_SI_CONFORM_PATTERN may occur alone
__UNIT_SI_CONFORM_3 = rf"""
    {__UNIT_SYMBOLS_SI_CONFORM_PATTERN}
"""

__UNIT_SI_CONFORM_PATTERN = rf"""
    (?:{__UNIT_SI_CONFORM_1}
    |{__UNIT_SI_CONFORM_2}
    |{__UNIT_SI_CONFORM_3})
"""

# __UNIT_SYMBOLS_SI_NOT_CONFORM_FOR_INFORMAL_SUFFIX_PATTERN may contain
# __UNIT_INFORMAL_PREFIX_PATTERN and __UNIT_INFORMAL_SUFFIX_PATTERN
__UNIT_SI_NOT_CONFORM_1 = rf"""
    {__UNIT_INFORMAL_PREFIX_PATTERN}?
    {__UNIT_SYMBOLS_SI_NOT_CONFORM_FOR_INFORMAL_SUFFIX_PATTERN}
    {__UNIT_INFORMAL_SUFFIX_PATTERN}?
"""

# __UNIT_SYMBOLS_SI_NOT_CONFORM_FOR_INFORMAL_PREFIX_PATTERN may contain
# __UNIT_INFORMAL_PREFIX_PATTERN
__UNIT_SI_NOT_CONFORM_2 = rf"""
    {__UNIT_INFORMAL_PREFIX_PATTERN}?
    {__UNIT_SYMBOLS_SI_NOT_CONFORM_FOR_INFORMAL_PREFIX_PATTERN}
"""

# __UNIT_SYMBOLS_SI_NOT_CONFORM_PATTERN must not use __UNIT_SI_PREFIX_PATTERN

# __UNIT_SYMBOLS_SI_NOT_CONFORM_FOR_EXPONENTS_PATTERN may contain
# __UNIT_SI_SUFFIX_PATTERN
__UNIT_SI_NOT_CONFORM_3 = rf"""
    {__UNIT_SYMBOLS_SI_NOT_CONFORM_FOR_EXPONENTS_PATTERN}?
    {__UNIT_SI_SUFFIX_PATTERN}
"""

# __UNIT_SYMBOLS_SI_NOT_CONFORM_PATTERN may occur alone
__UNIT_SI_NOT_CONFORM_4 = rf"""
    {__UNIT_SYMBOLS_SI_NOT_CONFORM_PATTERN}
"""

__UNIT_SI_NOT_CONFORM_PATTERN = rf"""
    (?:{__UNIT_SI_NOT_CONFORM_1}
        |{__UNIT_SI_NOT_CONFORM_2}
        |{__UNIT_SI_NOT_CONFORM_3}
        |{__UNIT_SI_NOT_CONFORM_4})
"""

__UNIT_VARIANT_PATTERN = rf"""
    (?:{__UNIT_SI_CONFORM_PATTERN}
        |{__UNIT_SI_NOT_CONFORM_PATTERN})
"""

__UNIT_MATHEMATICAL_OPERATORS_PATTERN = r"[\u00B7\u002F]"
__UNIT_LOOK_AHEAD_PATTERN = r"((?<=[\W\d])|^)"
__UNIT_LOOK_AHEAD_WITHOUT_SPACE_PATTERN = r"(?<=\d)"
__UNIT_LOOK_BEHIND_PATTERN = r"(?:(?=[^\w\u00B7\u002F])|$)"
__UNIT_MULTIPLE_SPACES = r"(?:\s{2,})"

def __re_compile(expression: str) -> re.Pattern:
    return re.compile(
        re.sub(
        r"\s{2,}|[\r\n]+",
        "",
        expression)
    )

UNIT_PATTERN = __re_compile(rf"""
    {__UNIT_LOOK_AHEAD_PATTERN}
    ({__UNIT_VARIANT_PATTERN}
        (?:{__UNIT_MATHEMATICAL_OPERATORS_PATTERN}
            {__UNIT_VARIANT_PATTERN})*)
    {__UNIT_LOOK_BEHIND_PATTERN}
""")

UNIT_WITHOUT_SPACE_PATTERN = __re_compile(rf"""
    {__UNIT_LOOK_AHEAD_WITHOUT_SPACE_PATTERN}
    {__UNIT_VARIANT_PATTERN}
    (?:{__UNIT_MATHEMATICAL_OPERATORS_PATTERN}
        {__UNIT_VARIANT_PATTERN})*
    {__UNIT_LOOK_BEHIND_PATTERN}
""")

__UNIT_WITH_MULTIPLE_SPACES_PATTERN = __re_compile(rf"""
    {__UNIT_LOOK_AHEAD_PATTERN}
    ({__UNIT_MULTIPLE_SPACES})
    ({__UNIT_VARIANT_PATTERN}
        (?:{__UNIT_MATHEMATICAL_OPERATORS_PATTERN}
            {__UNIT_VARIANT_PATTERN})*)
    {__UNIT_LOOK_BEHIND_PATTERN}
""")

def units(text: str) -> list[str]:
    pass

def normalize(text: str) -> str:
    text = UNIT_WITHOUT_SPACE_PATTERN.sub(
        lambda match: " " + match.group(0),
        text
    )
    text = __UNIT_WITH_MULTIPLE_SPACES_PATTERN.sub(
        lambda match: " " + match.group(3),
        text
    )
    return text
