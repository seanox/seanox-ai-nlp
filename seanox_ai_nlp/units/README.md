## Description

In everyday language, measurements are typically expressed as a combination of
numerical value and unit -- such as __1000 hPa__, __50 km/h__ or __-20.5
&ordm;C__. These expressions appear in weather reports, product descriptions,
medical statements, social media posts and more -- often with inconsistent
formatting or informal phrasing.

This module is intended for developers and NLP practitioners seeking to extract
measurement expressions from natural language.

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

| Unit                       | Symbol&nbsp;&blacktriangledown; | Classification           | SI Base | SI Derivation | SI Extension | SI relevant | SI with Prefix | SI with Exponents | Common Units | Informal Variant |
|----------------------------|---------------------------------|--------------------------|---------|---------------|--------------|-------------|----------------|-------------------|--------------|------------------|
| Foot (single quote mark)   | '                               | Length                   |         |               |              |             |                |                   | x            |                  |
| Inch (double quote mark)   | "                               | Length                   |         |               |              |             |                |                   | x            |                  |
| Percent                    | %                               | Ratio                    |         |               |              |             |                |                   | x            |                  |
| (Arc) Minute               | &#x2032;                        | Angle                    |         |               |              |             |                |                   | x            |                  |
| (Arc) Second               | &#x2033;                        | Angle                    |         |               |              |             |                |                   | x            |                  |
| Inch (quote mark)          | &#x2033;                        | Length                   |         |               |              |             |                |                   | x            |                  |
| Ampere                     | A                               | Electricity              | x       |               |              | x           | x              | x                 |              |                  |
| Are                        | a                               | Area                     |         |               | x            | x           |                |                   | x            |                  |
| Year                       | a                               | Time                     |         |               |              |             |                |                   | x            |                  |
| Astronomical Unit          | AE                              | Astronomy, Length        |         |               | x            | x           | x              |                   |              |                  |
| Battery Capacity           | Ah                              | Electricity              |         |               | x            | x           |                |                   | x            |                  |
| Atmosphere (pressure)      | atm                             | Pressure                 |         |               |              |             |                |                   | x            |                  |
| Gauge Pressure             | At&uuml;                        | Pressure                 |         |               |              |             |                |                   | x            |                  |
| Astronomical Unit          | AU                              | Astronomy, Length        |         |               | x            | x           | x              |                   |              |                  |
| Barn                       | b                               | Area, Radiation          |         |               | x            | x           | x              |                   |              |                  |
| Bel                        | B                               | Acoustics                |         |               | x            | x           |                |                   | x            |                  |
| Bar                        | bar                             | Pressure                 |         |               | x            | x           |                |                   | x            |                  |
| Barrel (oil)               | bbl                             | Volume                   |         |               |              |             |                |                   | x            |                  |
| Becquerel                  | Bq                              | Radiation                |         | x             |              | x           | x              | x                 |              |                  |
| Coulomb                    | C                               | Electricity              |         | x             |              | x           | x              | x                 |              |                  |
| Candela                    | cd                              | Light                    | x       |               |              | x           | x              |                   |              |                  |
| Carat (gem weight)         | ct                              | Mass                     |         |               | x            | x           | x              |                   |              |                  |
| Day                        | d                               | Time                     |         |               | x            | x           |                |                   | x            |                  |
| Dalton                     | Da                              | Mass, Atomic             |         |               | x            | x           | x              |                   |              |                  |
| Decameter                  | dam                             | Length                   |         |               |              |             |                |                   | x            |                  |
| Decibel                    | dB                              | Acoustics                |         |               | x            | x           |                |                   | x            |                  |
| Decibel A/C/G/Z curve      | db([ACGZ])                      | Acoustics                |         |               | x            | x           |                |                   | x            |                  |
| Dioptre                    | dpt                             | Optics                   |         |               | x            | x           |                |                   | x            |                  |
| Double Hundredweight       | dz                              | Quantity                 |         |               |              |             |                |                   | x            |                  |
| Dozen                      | dz                              | Quantity                 |         |               |              |             |                |                   | x            |                  |
| Electronvolt               | eV                              | Energy                   |         |               | x            | x           | x              |                   |              |                  |
| Farad                      | F                               | Electricity, Capacitance |         | x             |              | x           | x              | x                 |              |                  |
| Foot                       | ft                              | Length                   |         |               |              |             |                |                   | x            | x                |
| Gram                       | g                               | Mass                     | x       |               |              | x           | x              | x                 |              |                  |
| Gallon                     | gal                             | Volume                   |         |               |              |             |                |                   | x            |                  |
| Gray                       | Gy                              | Radiation                |         | x             |              | x           | x              |                   |              |                  |
| Henry                      | H                               | Electricity              |         | x             |              | x           | x              | x                 |              |                  |
| Hour                       | h                               | Time                     |         |               | x            | x           | x              |                   |              |                  |
| Hectare                    | ha                              | Area                     |         |               | x            | x           |                |                   | x            |                  |
| Horsepower (imperial)      | hp                              | Power                    |         |               |              |             |                |                   | x            |                  |
| Hertz                      | Hz                              | Frequency                |         | x             |              | x           | x              |                   |              |                  |
| Inch                       | in                              | Length                   |         |               |              |             |                |                   | x            | x                |
| Joule                      | J                               | Energy                   |         | x             |              | x           | x              | x                 |              |                  |
| Kelvin                     | K                               | Temperature              | x       |               |              | x           | x              |                   |              |                  |
| Katal                      | kat                             | Amount                   |         | x             |              | x           | x              | x                 |              |                  |
| Knot                       | kn                              | Speed                    |         |               | x            | x           |                |                   | x            |                  |
| Karat (gold purity)        | kt                              | Mass                     |         |               |              |             |                |                   | x            |                  |
| Knot                       | kt                              | Speed                    |         |               | x            | x           |                |                   | x            |                  |
| Liter                      | l                               | Volume                   |         |               | x            | x           | x              | x                 |              |                  |
| Liter                      | L                               | Volume                   |         |               | x            | x           | x              | x                 |              |                  |
| Pound                      | lb                              | Mass                     |         |               |              |             |                |                   | x            |                  |
| Light-year                 | lj                              | Length, Astronomy        |         |               |              |             |                |                   | x            |                  |
| Lumen                      | lm                              | Light                    |         | x             |              | x           | x              | x                 |              |                  |
| Lumen second               | ls                              | Light, Energy            |         |               |              |             |                |                   | x            |                  |
| Lux                        | lx                              | Light                    |         | x             |              | x           | x              | x                 |              |                  |
| Meter                      | m                               | Length                   | x       |               |              | x           | x              | x                 |              | x                |
| Mel                        | mel                             | Acoustics                |         |               | x            | x           |                |                   | x            |                  |
| Mile                       | mi                              | Length                   |         |               |              |             |                |                   | x            | x                |
| Mile                       | mile                            | Length                   |         |               |              |             |                |                   |              | x                |
| Minute (long form)         | min                             | Time                     |         |               | x            | x           |                |                   | x            |                  |
| Mole                       | mol                             | Amount                   | x       |               |              | x           | x              | x                 |              |                  |
| Newton                     | N                               | Force                    |         | x             |              | x           | x              |                   |              |                  |
| Neper                      | Np                              | Acoustics                |         |               | x            | x           |                |                   | x            |                  |
| Degree                     | &ordm;                          | Angle                    |         |               |              |             |                |                   | x            |                  |
| Degree Celsius             | &ordm;C                         | Temperature              |         | x             |              | x           |                |                   | x            |                  |
| Ounce                      | oz                              | Mass                     |         |               |              |             |                |                   | x            |                  |
| Ounce                      | oz.                             | Mass                     |         |               |              |             |                |                   | x            |                  |
| Troy Ounce                 | oz. tr.                         | Mass                     |         |               | x            | x           | x              |                   |              |                  |
| Pond (metric force)        | p                               | Force                    |         |               |              |             |                |                   | x            |                  |
| Pascal                     | Pa                              | Pressure                 |         | x             |              | x           | x              | x                 |              |                  |
| Parsec                     | pc                              | Length, Astronomy        |         |               |              |             |                |                   | x            |                  |
| Horsepower (metric)        | PS                              | Power                    |         |               | x            | x           |                |                   | x            |                  |
| Pint                       | pt                              | Volume                   |         |               | x            | x           |                |                   | x            |                  |
| Radian                     | rad                             | Angle                    |         | x             |              | x           | x              |                   |              |                  |
| Cubic Meter (stacked wood) | rm                              | Volume                   |         |               |              |             |                |                   | x            |                  |
| Second (long form)         | s                               | Time                     | x       |               |              | x           | x              | x                 |              |                  |
| Siemens                    | S                               | Electricity, Conductance |         | x             |              | x           | x              | x                 |              |                  |
| Sone                       | sone                            | Acoustics                |         |               | x            | x           |                |                   | x            |                  |
| Steradian                  | sr                              | Angle                    |         | x             |              | x           | x              | x                 |              |                  |
| Stere (wood volume)        | St                              | Volume                   |         |               |              |             |                |                   | x            |                  |
| Sievert                    | Sv                              | Radiation                |         | x             |              | x           | x              |                   |              |                  |
| Metric Ton                 | t                               | Mass                     |         |               |              |             | x              |                   |              |                  |
| Tesla                      | T                               | Magnetic Field           |         | x             |              | x           | x              | x                 |              |                  |
| Tex                        | tex                             | Mass                     |         |               | x            | x           |                |                   | x            |                  |
| Atomic Mass Unit           | u                               | Mass, Atomic             |         |               |              |             |                |                   | x            |                  |
| Volt                       | V                               | Electricity              |         | x             |              | x           | x              | x                 |              |                  |
| Apparent Power             | VA                              | Electricity, Power       |         |               | x            | x           | x              |                   |              |                  |
| Reactive Power             | Var                             | Electricity, Power       |         |               |              |             |                |                   | x            |                  |
| Watt                       | W                               | Power                    |         | x             |              | x           | x              | x                 |              |                  |
| Weber                      | Wb                              | Magnetism                |         | x             |              | x           | x              | x                 |              |                  |
| Energy                     | Wh                              | Energy                   |         |               | x            | x           | x              |                   |              |                  |
| Yard                       | yd                              | Length                   |         |               |              |             |                |                   | x            | x                |
| Hundredweight (metric)     | Z                               | Mass                     |         |               |              |             |                |                   | x            |                  |
| Angular Frequency          | &omega;                         | Frequency, Rotation      |         |               |              |             |                |                   | x            |                  |
| Ohm                        | &Omega;                         | Electricity              |         | x             |              | x           | x              | x                 |              |                  |

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
