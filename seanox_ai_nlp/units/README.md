## Description

In everyday language, measurements are typically expressed as a combination of
numerical value and unit -- such as __1000 hPa__, __50 km/h__ or __-20.5
&ordm;C__. These expressions appear in weather reports, product descriptions,
medical statements, social media posts and more -- often with inconsistent
formatting or informal phrasing.

This module is intended for developers and NLP practitioners seeking to extract
measurement expressions from natural language -- without relying on large
language models (LLMs). It provides a rule-based, deterministic approach,
__aligned with lightweight, transparent, and production-grade NLP workflows__.

__units__ is a parser module designed to extract measurement expressions from
natural language text. It identifies numeric-unit constructs across general,
semi-technical, and academic contexts -- independent of language or formatting
conventions.

Extracted expressions are returned as structured entities, including:

- __UnitValue__ combinations of numerical values with measurement units  
- __Unit__ standalone unit references without associated values  

The module supports various number formats such as decimals, negative values,
scientific notation, and compound dimensions like __50 × 30 × 20 cm__. Spacing
between values and units is automatically optimized (e.g. transforming __20kg__
into __20 kg__), and composite measurement constructs are semantically segmented
for deeper analysis.

Ideal for integration into NLP workflows such as with spaCy’s __EntityRuler__,
and downstream tasks like semantic analysis or data normalization.

## Example

```python
from seanox_ai_nlp.units import units

print(units(
    "The cruising speed of the Boeing 747 is approximately 900 km/h (559 mph)."
    "It is typically expressed in kilometers per hour (km/h) and miles per hour (mph)."
))
```

```json
[
  {
    "label": "UNIT-VALUE",
    "start": 54,
    "end": 62,
    "text": "900 km/h",
    "value": "900",
    "unit": "km/h",
    "categories": ["length", "time"]
  },
  {
    "label": "UNIT-VALUE",
    "start": 64,
    "end": 73,
    "text": "559 mph",
    "value": "559",
    "unit": "mph",
    "categories": ["length", "time"]
  },
  {
    "label": "UNIT",
    "start": 99,
    "end": 101,
    "text": "in",
    "unit": "in",
    "categories": ["length"]
  },
  {
    "label": "UNIT",
    "start": 123,
    "end": 127,
    "text": "km/h",
    "unit": "km/h",
    "categories": ["length", "time"]
  },
  {
    "label": "UNIT",
    "start": 149,
    "end": 152,
    "text": "mph",
    "unit": "mph",
    "categories": ["length", "time"]
  }
]
```

__Unit Extraction Note__

The module identifies units and values using rule-based pattern recognition. In
the preceding example, the word __in__ is extracted as a unit __(inch)__, even
though it is used as a preposition in the context.

Since the module does __not perform semantic analysis__, such edge cases are
extracted __context-free__. Semantic interpretation is intentionally delegated to
the application layer -- typically based on:

- the presence of a __numeric value (value)__, if available
- and the assigned __categories (categories)__, such as __length__ or __time__

For example, an entry like __15 in__ can be interpreted as a valid unit
__(inch)__, while a standalone __in__ without a value or matching context may be
treated as a preposition.

This separation ensures the module remains robust, transparent, and adaptable to
different use cases.

# Table Of Contents
- [Description](#description)
  - [Numeric Value](#numeric-value)
  - [Symbolic Separator](#symbolic-separator)
  - [Numerical Signs](#numerical-signs)
  - [Units](#units)
  - [SI Prefixes for Multiples & Parts](#si-prefixes-for-multiples--parts)
  - [SI Suffix for Exponents](#si-suffix-for-exponents)
  - [Mathematical Operators](#mathematical-operators)
  - [Informal Prefix & Suffix](#informal-prefix--suffix-)
- [Installation & Setup](#installation--setup)
- [Maintenance](#maintenance)
- [Usage](#usage)
  - [`UNIT_PATTERN`](#unit_pattern)
  - [`NUMERIC_UNIT_PATTERN`](#numeric_unit_pattern)
  - [`UnitValue`](#unitvalue)
  - [`Unit`](#unit)
  - [`UnitEntry`](#unitentry)
  - [`units(text: str) -> list\[UnitEntry\]`](#unitstext-str---listunitentry)
  - [`SpacingModel`](#spacingmode)
  - [`spacing(text: str) -> str`](#spacingtext-str-mode-spacingmodespacingmodenumeric---str)
- [Links](#links) 

Below are the details in tables that show the basis of the regular expressions
used.

## Numeric Value
TODO:

| Locale  | Sign         | Format                   | 
|---------|--------------|--------------------------|
| CH      | + - &plusmn; | 1&rsquo;000&rsquo;000,00 |
| DE      | + - &plusmn; | 1.000.000,00             |
| EN      | + - &plusmn; | 1,000,000.00             |
| neutral | + - &plusmn; | 1000000.00               |

## Symbolic Separator

Symbolic separators link numerical values to compact measurements such as __10
&times; 20 &times; 30 cm__.

| Separator                   | Symbol   |
|-----------------------------|----------|
| Plus                        | +        |
| Minus                       | -        |
| Plus-minus / Tolerance      | &plusmn; |
| Asterisk / Multiplication   | *        |
| Times (Multiplication Sign) | &times;  |
| x / Times (ASCII)           | x        |
| Middle Dot / Dot Separator  | &middot; |
| Colon / Ratio               | :        |
| Divide Sign                 | &divide; |
| Slash / Division            | /        |
| Caret / Exponentiation      | ^        |
| En Dash / Range             | &ndash;  |

## Numerical Signs
Numerical signs are symbols that are placed before or alongside numerical
values -- especially in measurement data -- to express their meaning, accuracy,
or mathematical relationship.

| Operator                    | Symbol   |
|-----------------------------|----------|
| Plus                        | +        |
| Minus                       | -        |
| Plus-minus /<br/> tolerance | &plusmn; |
| Approx. / about             | ~        |

## Units

__Note__ These are base units only. Variants result from the additional
properties recorded (e.g. km as a combination of kilo and meter). There is no
claim to interpretation, classification, or complete standardization of the
units (e.g. [IEC](https://iec.ch/si), [BIPM](
    https://www.bipm.org/en/measurement-units)).

| Unit                        | Symbol&nbsp;&blacktriangledown; | Classification (Categories) | SI Base | SI Derivation | SI Extension | SI relevant | SI with Prefix | SI with Exponents | Common Units | Informal |
|-----------------------------|---------------------------------|-----------------------------|---------|---------------|--------------|-------------|----------------|-------------------|--------------|----------|
| Foot (single quote mark)    | '                               | length                      |         |               |              |             |                |                   | x            |          |
| Inch (double quote mark)    | "                               | length                      |         |               |              |             |                |                   | x            |          |
| Percent                     | %                               | ratio                       |         |               |              |             |                |                   | x            |          |
| Foot (quote mark)           | &#x2032;                        | length                      |         |               |              |             |                |                   | x            |          |
| Inch (quote mark)           | &#x2033;                        | length                      |         |               |              |             |                |                   | x            |          |
| Ampere                      | A                               | electricity                 | x       |               |              | x           | x              | x                 |              |          |
| Are                         | a                               | area                        |         |               | x            | x           |                |                   | x            |          |
| Astronomical Unit           | AE                              | astronomy length            |         |               | x            | x           | x              |                   |              |          |
| Battery Capacity            | Ah                              | electricity                 |         |               | x            | x           |                |                   | x            |          |
| Atmosphere (pressure)       | atm                             | pressure                    |         |               |              |             |                |                   | x            |          |
| Gauge Pressure              | At&uuml;                        | pressure                    |         |               |              |             |                |                   | x            |          |
| Astronomical Unit           | AU                              | astronomy length            |         |               | x            | x           | x              |                   |              |          |
| Barn                        | b                               | area radiation              |         |               | x            | x           | x              |                   |              |          |
| Bel                         | B                               | acoustics                   |         |               | x            | x           |                |                   | x            |          |
| Bar                         | bar                             | pressure                    |         |               | x            | x           |                |                   | x            |          |
| Barrel (oil)                | bbl                             | volume                      |         |               |              |             |                |                   | x            |          |
| Becquerel                   | Bq                              | radiation                   |         | x             |              | x           | x              | x                 |              |          |
| Coulomb                     | C                               | electricity                 |         | x             |              | x           | x              | x                 |              |          |
| Candela                     | cd                              | light                       | x       |               |              | x           | x              |                   |              |          |
| Carat (gem weight)          | ct                              | mass                        |         |               | x            | x           | x              |                   |              |          |
| Day                         | d                               | time                        |         |               | x            | x           |                |                   | x            |          |
| Dalton                      | Da                              | mass atomic                 |         |               | x            | x           | x              |                   |              |          |
| Decameter                   | dam                             | length                      |         |               |              |             |                |                   | x            |          |
| Decibel                     | dB                              | acoustics                   |         |               | x            | x           |                |                   | x            |          |
| Decibel A curve             | db(A)                           | acoustics                   |         |               | x            | x           |                |                   | x            |          |
| Decibel C curve             | db(C)                           | acoustics                   |         |               | x            | x           |                |                   | x            |          |
| Decibel G curve             | db(G)                           | acoustics                   |         |               | x            | x           |                |                   | x            |          |
| Decibel Z curve             | db(Z)                           | acoustics                   |         |               | x            | x           |                |                   | x            |          |
| Dioptre                     | dpt                             | optics                      |         |               | x            | x           |                |                   | x            |          |
| Double Hundredweight        | dz                              | quantity                    |         |               |              |             |                |                   | x            |          |
| Dozen                       | dz                              | quantity                    |         |               |              |             |                |                   | x            |          |
| Electronvolt                | eV                              | energy                      |         |               | x            | x           | x              |                   |              |          |
| Farad                       | F                               | electricity capacitance     |         | x             |              | x           | x              | x                 |              |          |
| Foot                        | ft                              | length                      |         |               |              |             |                |                   | x            | x        |
| Gram                        | g                               | mass                        | x       |               |              | x           | x              | x                 |              |          |
| Gallon                      | gal                             | volume                      |         |               |              |             |                |                   | x            |          |
| Gray                        | Gy                              | radiation                   |         | x             |              | x           | x              |                   |              |          |
| Henry                       | H                               | electricity                 |         | x             |              | x           | x              | x                 |              |          |
| Hour                        | h                               | time                        |         |               | x            | x           | x              |                   |              |          |
| Hectare                     | ha                              | area                        |         |               | x            | x           |                |                   | x            |          |
| Horsepower (imperial)       | hp                              | power                       |         |               |              |             |                |                   | x            |          |
| Hertz                       | Hz                              | frequency                   |         | x             |              | x           | x              |                   |              |          |
| Inch                        | in                              | length                      |         |               |              |             |                |                   | x            | x        |
| Joule                       | J                               | energy                      |         | x             |              | x           | x              | x                 |              |          |
| Kelvin                      | K                               | temperature                 | x       |               |              | x           | x              |                   |              |          |
| Katal                       | kat                             | amount                      |         | x             |              | x           | x              | x                 |              |          |
| Knot                        | kn                              | speed                       |         |               | x            | x           |                |                   | x            |          |
| Karat (gold purity)         | kt                              | mass                        |         |               |              |             |                |                   | x            |          |
| Knot                        | kt                              | speed                       |         |               | x            | x           |                |                   | x            |          |
| Liter                       | l                               | volume                      |         |               | x            | x           | x              | x                 |              |          |
| Liter                       | L                               | volume                      |         |               | x            | x           | x              | x                 |              |          |
| Pound                       | lb                              | mass                        |         |               |              |             |                |                   | x            |          |
| Light-year                  | lj                              | length astronomy            |         |               |              |             |                |                   | x            |          |
| Lumen                       | lm                              | light                       |         | x             |              | x           | x              | x                 |              |          |
| Lumen second                | ls                              | light energy                |         |               |              |             |                |                   | x            |          |
| Lux                         | lx                              | light                       |         | x             |              | x           | x              | x                 |              |          |
| Meter                       | m                               | length                      | x       |               |              | x           | x              | x                 |              | x        |
| Mel                         | mel                             | acoustics                   |         |               | x            | x           |                |                   | x            |          |
| Mile                        | mi                              | length                      |         |               |              |             |                |                   | x            | x        |
| Mile                        | mile                            | length                      |         |               |              |             |                |                   |              | x        |
| Minute (long form)          | min                             | time                        |         |               | x            | x           |                |                   | x            |          |
| Mole                        | mol                             | amount                      | x       |               |              | x           | x              | x                 |              |          |
| Miles per Hour              | mph                             | length time                 |         |               |              |             |                |                   |              | x        |
| Newton                      | N                               | force                       |         | x             |              | x           | x              |                   |              |          |
| Neper                       | Np                              | acoustics                   |         |               | x            | x           |                |                   | x            |          |
| Degree                      | &ordm;                          | angle                       |         |               |              |             |                |                   | x            |          |
| Degree Celsius              | &ordm;C                         | temperature                 |         | x             |              | x           |                |                   | x            |          |
| Ounce                       | oz                              | mass                        |         |               |              |             |                |                   | x            |          |
| Ounce                       | oz.                             | mass                        |         |               |              |             |                |                   | x            |          |
| Troy Ounce                  | oz. tr.                         | mass                        |         |               | x            | x           | x              |                   |              |          |
| Pond (metric force)         | p                               | force                       |         |               |              |             |                |                   | x            |          |
| Pascal                      | Pa                              | pressure                    |         | x             |              | x           | x              | x                 |              |          |
| Parsec                      | pc                              | length astronomy            |         |               |              |             |                |                   | x            |          |
| Horsepower (metric)         | PS                              | power                       |         |               | x            | x           |                |                   | x            |          |
| Pint                        | pt                              | volume                      |         |               | x            | x           |                |                   | x            |          |
| Radian                      | rad                             | angle                       |         | x             |              | x           | x              |                   |              |          |
| Cubic Meter (stacked wood)  | rm                              | volume                      |         |               |              |             |                |                   | x            |          |
| Second (long form)          | s                               | time                        | x       |               |              | x           | x              | x                 |              |          |
| Siemens                     | S                               | electricity conductance     |         | x             |              | x           | x              | x                 |              |          |
| Sone                        | sone                            | acoustics                   |         |               | x            | x           |                |                   | x            |          |
| Steradian                   | sr                              | angle                       |         | x             |              | x           | x              | x                 |              |          |
| Stere (wood volume)         | St                              | volume                      |         |               |              |             |                |                   | x            |          |
| Sievert                     | Sv                              | radiation                   |         | x             |              | x           | x              |                   |              |          |
| Metric Ton                  | t                               | mass                        |         |               |              |             | x              |                   |              |          |
| Tesla                       | T                               | magnetic field              |         | x             |              | x           | x              | x                 |              |          |
| Tex                         | tex                             | mass                        |         |               | x            | x           |                |                   | x            |          |
| Atomic Mass Unit            | u                               | mass atomic                 |         |               |              |             |                |                   | x            |          |
| Volt                        | V                               | electricity                 |         | x             |              | x           | x              | x                 |              |          |
| Apparent Power              | VA                              | electricity power           |         |               | x            | x           | x              |                   |              |          |
| Reactive Power              | Var                             | electricity power           |         |               |              |             |                |                   | x            |          |
| Watt                        | W                               | power                       |         | x             |              | x           | x              | x                 |              |          |
| Weber                       | Wb                              | magnetism                   |         | x             |              | x           | x              | x                 |              |          |
| Energy                      | Wh                              | energy                      |         |               | x            | x           | x              |                   |              |          |
| Yard                        | yd                              | length                      |         |               |              |             |                |                   | x            | x        |
| Hundredweight (metric)      | Z                               | mass                        |         |               |              |             |                |                   | x            |          |
| Angular Frequency           | &omega;                         | frequency rotation          |         |               |              |             |                |                   | x            |          |
| Ohm                         | &Omega;                         | electricity                 |         | x             |              | x           | x              | x                 |              |          |


The units and prefixes included were compiled from publicly available sources,
including technical references (e.g. Wikipedia, national standards, product
catalogs), as well as commonly observed usage. In the absence of a unified
standard, this dataset aims to offer a practical and extensible collection
rather than a formally authoritative one.

## SI Prefixes for Multiples & Parts
TODO:

| Positive Powers | Symbol | Negative Powers | Symbol  |
|-----------------|--------|-----------------|---------|
| Quetta          | Q      | Dezi            | d       |
| Ronna           | R      | Zenti           | c       |
| Yotta           | Y      | Milli           | m       |
| Zetta           | Z      | Mikro           | &micro; |
| Exa             | E      | Nano            | n       |
| Peta            | P      | Piko            | p       |
| Tera            | T      | Femto           | f       |
| Giga            | G      | Atto            | a       |
| Mega            | M      | Zepto           | z       |
| Kilo            | k      | Yokto           | y       |
| Hekto           | h      | Ronto           | r       |
| Deka            | da     | Quekto          | q       |

## SI Suffix for Exponents
TODO:

| Positive Suffix | Negative Suffix |
|-----------------|-----------------|
| &sup1;          | &#x207B;&sup1;  |
| &sup2;          | &#x207B;&sup2;  |
| &sup3;          | &#x207B;&sup3;  |

## Mathematical Operators
TODO:

| Operator                                | Symbol   |
|-----------------------------------------|----------|
| Asterisk                                | *        |
| Division sign /<br/> Slash              | &sol;    |
| Letter x                                | x        |
| Multiplication point /<br/>Center point | &middot; |
| Multiplication sign                     | &times;  |
| Multiplication sign                     | &times;  |

## Informal Prefix & Suffix 
TODO:

| Prefix       | Symbol | Suffix | Symbol | 
|--------------|--------|--------|--------|
| Cubic        | c      | Cubic  | 2      |
| Square (lat) | q      | Square | 3      |

# Installation & Setup
TODO:

## Maintenance

The parser is based on a rule-driven approach using regular expressions
(__RegEx__). The definition values and aggregated patterns for unit extraction
are centrally maintained in the file `units.xlsx`.

- The Excel spreadsheet contains the basic data (e.g., units, classification,
  ...) and also precompiles the RegEx expressions as constants for parsing.
- These constants with the precompiled expressions then replace the existing
  constants  in  `units.py` .
- __units__ is designed to use the updated expressions at runtime -- enabling
  flexible maintenance and extendability of the extraction logic without
  modifying the source code.

System maintenance primarily involves updating the `units.xlsx` table. Changes
made there directly affect parser performance, without requiring manual
alterations in the Python implementation.

# Usage
TODO:

## `UNIT_PATTERN`
TODO:

## `NUMERIC_UNIT_PATTERN`
TODO:

## `UnitValue`
TODO:

## `Unit`
TODO:

## `UnitEntry`
TODO:

## `units(text: str) -> list\[UnitEntry\]`
TODO:

## `SpacingMode`
TODO:

## `spacing(text: str, mode: SpacingMode=SpacingMode.NUMERIC) -> str`
TODO:

# Links

References to the sources that contributed to the content of the page, among
other things.

- https://de.wikipedia.org/wiki/Internationales_Einheitensystem
- https://de.wikipedia.org/wiki/Gebr%C3%A4uchliche_Nicht-SI-Einheiten
- https://www.taschenhirn.de/aktuelles-allgemeinwissen/liste-masseinheiten-formeln/
- https://www.tablesgenerator.com/markdown_tables
