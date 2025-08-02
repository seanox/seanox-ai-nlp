## Description

In natural language, __measurements__ are usually expressed as a combination of
a __numerical value__ and a __unit__ (e.g. _-20.5 &ordm;C_, _1000 hPa_,
_50 km/h_).

__units__ supports the extraction of __language-neutral measurements__ from
natural texts as __structured entities__, as well as the __optimization of
measurement formatting__.

When extracting measurements, units always __returns two entities__ per match:
- combined units with values (__UNIT-VALUE__)
- pure units of measurement (__UNIT__)

Various __number formats__ are supported, including:
- __decimal values__
- __negative values__
- __positive and negative exponents__
- __compound units__

The entities are extracted in a __structured manner__ to facilitate their
__further processing__ and __formatting__ in __processing pipelines__ -- e.g.
using an __EntityRuler__ in __spaCy__ -- as well as in __downstream
applications__.

The units are __common language-independent basic units__ that typically occur
in __natural sentences__ -- from __everyday contexts__ to __slightly technical__
or __slightly academic contexts__. This includes __informal prefixes__ and
__informal suffixes__ that may occur in __informal or non-standard contexts__.

# Table Of Contents
- [Description](#description)
  - [Numeric Value](#numeric-value)
  - [Units](#units)
  - [SI Prefixes for Multiples & Parts](#si-prefixes-for-multiples--parts)
  - [SI Suffix for Exponents](#si-suffix-for-exponents)
  - [Mathematical Operators](#mathematical-operators)
  - [Informal Prefix & Suffix](#informal-prefix--suffix-)
- [Installation & Setup](#installation--setup)
- [Usage](#usage)
  - [`UNIT_PATTERN`](#unit_pattern)
  - [`NUMERIC_UNIT_PATTERN`](#numeric_unit_pattern)
  - [`UnitValue`](#unitvalue)
  - [`Unit`](#unit)
  - [`UnitEntry`](#unitentry)
  - [`units(text: str) -> list\[UnitEntry\]`](#unitstext-str---listunitentry)
  - [`normalize(text: str) -> str`](#normalizetext-str---str)
- [Links](#links) 

Below are the details in tables that show the basis of the regular expressions
used.

## Numeric Value
| Locale  | __Sign__     | __Format__               | 
|---------|--------------|--------------------------|
| CH      | + - &plusmn; | 1&rsquo;000&rsquo;000,00 |
| DE      | + - &plusmn; | 1.000.000,00             |
| EN      | + - &plusmn; | 1,000,000.00             |
| neutral | + - &plusmn; | 1000000.00               |

## Units
__Note__ These are base units only. Variants result from the additional
properties recorded (ee.g. km as a combination of kilo and meter). There is no
claim to interpretation, classification, or complete standardization of the
units (e.g. [IEC](https://iec.ch/si), [BIPM](https://www.bipm.org/en/measurement-units)).

| Unit                       | Symbol&nbsp;&blacktriangledown; | SI Base | SI Derivation | SI Extension | SI relevant | SI Prefix | SI Exponents | Common Units | Informal Phrase | Informal Prefix | Informal Exponents |
|----------------------------|---------------------------------|---------|---------------|--------------|-------------|-----------|--------------|--------------|-----------------|-----------------|--------------------|
| (Arc) Minute               | &#x2032;                        |         |               |              |             |           |              | x            |                 |                 |                    |
| Inch (quote mark)          | &#x2033;                        |         |               |              |             |           |              | x            |                 |                 |                    |
| (Arc) Second               | &#x2033;                        |         |               |              |             |           |              | x            |                 |                 |                    |
| Acceleration               | a                               |         |               |              |             |           |              | x            |                 |                 |                    |
| Ampere                     | A                               | x       |               |              | x           | x         | x            |              |                 |                 |                    |
| Are                        | a                               |         |               | x            | x           |           |              | x            |                 | x               | x                  |
| Year                       | a                               |         |               |              |             |           |              | x            |                 |                 |                    |
| Astronomical Unit          | AE                              |         |               | x            | x           | x         |              |              |                 |                 |                    |
| Battery Capacity           | Ah                              |         |               | x            | x           |           |              | x            |                 |                 |                    |
| Atmosphere (pressure)      | atm                             |         |               |              |             |           |              | x            |                 |                 |                    |
| Gauge Pressure             | At&uuml;                        |         |               |              |             |           |              | x            |                 |                 |                    |
| Astronomical Unit          | AU                              |         |               | x            | x           | x         |              |              |                 |                 |                    |
| Barn                       | b                               |         |               | x            | x           | x         |              |              |                 |                 |                    |
| Bel                        | B                               |         |               | x            | x           | x         |              |              |                 |                 |                    |
| Bar                        | bar                             |         |               | x            | x           |           |              | x            |                 |                 |                    |
| Barrel (oil)               | bbl                             |         |               |              |             |           |              | x            |                 |                 |                    |
| Becquerel                  | Bq                              |         | x             |              | x           | x         | x            |              |                 |                 |                    |
| Coulomb                    | C                               |         | x             |              | x           | x         | x            |              |                 |                 |                    |
| Candela                    | cd                              | x       |               |              | x           | x         | x            |              |                 |                 |                    |
| Carat (gem weight)         | ct                              |         |               | x            | x           | x         |              |              |                 |                 |                    |
| Day                        | d                               |         |               | x            | x           |           |              | x            |                 |                 |                    |
| Dalton                     | Da                              |         |               | x            | x           | x         |              |              |                 |                 |                    |
| Decameter                  | dam                             |         |               |              |             |           |              | x            |                 |                 |                    |
| Decibel                    | dB                              |         |               | x            | x           |           |              | x            |                 |                 |                    |
| Decibel A curve            | db(A)                           |         |               | x            | x           |           |              | x            |                 |                 |                    |
| Decibel C curve            | db(C)                           |         |               | x            | x           |           |              | x            |                 |                 |                    |
| Decibel G curve            | db(G)                           |         |               | x            | x           |           |              | x            |                 |                 |                    |
| Decibel Z curve            | db(Z)                           |         |               | x            | x           |           |              | x            |                 |                 |                    |
| Dioptre                    | dpt                             |         |               | x            | x           |           |              | x            |                 |                 |                    |
| Double Hundredweight       | dz                              |         |               |              |             |           |              | x            |                 |                 |                    |
| Dozen                      | Dz                              |         |               |              |             |           |              | x            |                 |                 |                    |
| Electronvolt               | eV                              |         |               | x            | x           | x         |              |              |                 |                 |                    |
| Farad                      | F                               |         | x             |              | x           | x         | x            |              |                 |                 |                    |
| Foot                       | ft                              |         |               |              |             |           |              | x            |                 |                 |                    |
| Gram                       | g                               | x       |               |              | x           | x         |              |              |                 |                 |                    |
| Gallon                     | gal                             |         |               |              |             |           |              | x            |                 |                 |                    |
| Gray                       | Gy                              |         | x             |              | x           | x         | x            |              |                 |                 |                    |
| Henry                      | H                               |         | x             |              | x           | x         | x            |              |                 |                 |                    |
| Hour                       | h                               |         |               | x            | x           | x         |              |              |                 |                 |                    |
| Hectare                    | ha                              |         |               | x            | x           |           |              | x            |                 | x               | x                  |
| Hectoliter                 | hl                              |         |               |              |             |           |              | x            |                 |                 |                    |
| Horsepower (imperial)      | hp                              |         |               |              |             |           |              | x            |                 |                 |                    |
| Hertz                      | Hz                              |         | x             |              | x           | x         | x            |              |                 |                 |                    |
| Inch                       | in                              |         |               |              |             |           |              | x            |                 |                 |                    |
| Joule                      | J                               |         | x             |              | x           | x         | x            |              |                 |                 |                    |
| Kelvin                     | K                               | x       |               |              | x           | x         | x            |              |                 |                 |                    |
| Katal                      | kat                             |         | x             |              | x           | x         | x            |              |                 |                 |                    |
| Knot                       | kn                              |         |               | x            | x           |           |              | x            |                 |                 |                    |
| Karat (gold purity)        | kt                              |         |               |              |             |           |              | x            |                 |                 |                    |
| Knot                       | kt                              |         |               | x            | x           |           |              | x            |                 |                 |                    |
| Liter                      | l                               |         |               | x            | x           |           |              | x            |                 |                 |                    |
| Liter                      | L                               |         |               | x            | x           |           |              | x            |                 |                 |                    |
| Pound                      | lb                              |         |               |              |             |           |              | x            |                 |                 |                    |
| Light-year                 | lj                              |         |               |              |             |           |              | x            |                 |                 |                    |
| Lumen                      | lm                              |         | x             |              | x           | x         | x            |              |                 |                 |                    |
| Lumen second               | ls                              |         |               |              |             |           |              | x            |                 |                 |                    |
| Lux                        | lx                              |         | x             |              | x           | x         | x            |              |                 |                 |                    |
| Meter                      | m                               | x       |               |              | x           | x         | x            |              |                 | x               | x                  |
| Mel                        | mel                             |         |               | x            | x           |           |              | x            |                 |                 |                    |
| Mile                       | mi                              |         |               |              |             |           |              | x            |                 | x               | x                  |
| Minute (long form)         | min                             |         |               | x            | x           |           |              | x            |                 |                 |                    |
| Mole                       | mol                             | x       |               |              | x           | x         | x            |              |                 |                 |                    |
| Newton                     | N                               |         | x             |              | x           | x         |              |              |                 |                 |                    |
| Neper                      | Np                              |         |               | x            | x           |           |              | x            |                 |                 |                    |
| Degree                     | &ordm;                          |         |               |              |             |           |              | x            |                 |                 |                    |
| Degree Celsius             | &ordm;C                         |         | x             |              | x           | x         |              |              |                 |                 |                    |
| Ounce                      | oz                              |         |               |              |             |           |              | x            |                 |                 |                    |
| Ounce                      | oz.                             |         |               |              |             |           |              | x            |                 |                 |                    |
| Troy Ounce                 | oz. tr.                         |         |               | x            | x           | x         |              |              |                 |                 |                    |
| Pond (metric force)        | p                               |         |               |              |             |           |              | x            |                 |                 |                    |
| Pascal                     | Pa                              |         | x             |              | x           | x         | x            |              |                 |                 |                    |
| Parsec                     | pc                              |         |               |              |             |           |              | x            |                 |                 |                    |
| Horsepower (metric)        | PS                              |         |               | x            | x           |           |              | x            |                 |                 |                    |
| Pint                       | pt                              |         |               | x            | x           | x         |              |              |                 |                 |                    |
| Radian                     | rad                             |         | x             |              | x           |           |              | x            |                 |                 |                    |
| Cubic Meter (stacked wood) | rm                              |         |               |              |             |           |              | x            |                 |                 |                    |
| Second (long form)         | s                               | x       |               |              | x           | x         | x            |              |                 |                 |                    |
| Siemens                    | S                               |         | x             |              | x           | x         | x            |              |                 |                 |                    |
| Sone                       | sone                            |         |               | x            | x           |           |              | x            |                 |                 |                    |
| Square foot                | sq.ft.                          |         |               |              |             |           |              | x            | x               |                 |                    |
| Square inch                | sq.in.                          |         |               |              |             |           |              | x            | x               |                 |                    |
| Square mile                | sq.mile                         |         |               |              |             |           |              | x            | x               |                 |                    |
| Square yard                | sq.yd.                          |         |               |              |             |           |              | x            | x               |                 |                    |
| Square foot                | sq. ft.                         |         |               |              |             |           |              | x            | x               |                 |                    |
| Square inch                | sq. in.                         |         |               |              |             |           |              | x            | x               |                 |                    |
| Square mile                | sq. mile                        |         |               |              |             |           |              | x            | x               |                 |                    |
| Square yard                | sq. yd.                         |         |               |              |             |           |              | x            | x               |                 |                    |
| Square foot                | sq ft                           |         |               |              |             |           |              | x            | x               |                 |                    |
| Square inch                | sq in                           |         |               |              |             |           |              | x            | x               |                 |                    |
| Square mile                | sq mile                         |         |               |              |             |           |              | x            | x               |                 |                    |
| Square yard                | sq yd                           |         |               |              |             |           |              | x            | x               |                 |                    |
| Steradian                  | sr                              |         | x             |              | x           | x         | x            |              |                 |                 |                    |
| Stere (wood volume)        | St                              |         |               |              |             |           |              | x            |                 |                 |                    |
| Sievert                    | Sv                              |         | x             |              | x           | x         | x            |              |                 |                 |                    |
| Metric Ton                 | t                               |         |               |              |             |           |              | x            |                 |                 |                    |
| Tesla                      | T                               |         | x             |              | x           | x         | x            |              |                 |                 |                    |
| Tex                        | tex                             |         |               | x            | x           |           |              | x            |                 |                 |                    |
| Atomic Mass Unit           | u                               |         |               |              |             |           |              | x            |                 |                 |                    |
| Velocity                   | v                               |         |               |              |             |           |              | x            |                 |                 |                    |
| Volt                       | V                               |         | x             |              | x           | x         | x            |              |                 |                 |                    |
| Apparent Power             | VA                              |         |               | x            | x           |           |              | x            |                 |                 |                    |
| Reactive Power             | Var                             |         |               |              |             |           |              | x            |                 |                 |                    |
| Watt                       | W                               |         | x             |              | x           | x         | x            |              |                 |                 |                    |
| Weber                      | Wb                              |         | x             |              | x           | x         | x            |              |                 |                 |                    |
| Energy                     | Wh                              |         |               | x            | x           |           |              | x            |                 |                 |                    |
| Yard                       | yd                              |         |               |              |             |           |              | x            |                 |                 |                    |
| Hundredweight (metric)     | Z                               |         |               |              |             |           |              | x            |                 |                 |                    |
| Density                    | &rho;                           |         |               |              |             |           |              | x            |                 |                 |                    |
| Angular Frequency          | &omega;                         |         |               |              |             |           |              | x            |                 |                 |                    |
| Ohm                        | &Omega;                         |         | x             |              | x           | x         | x            |              |                 |                 |                    |

## SI Prefixes for Multiples & Parts
| __Positive Powers__ | __Symbol__ | __Negative Powers__ | __Symbol__ |
|---------------------|------------|---------------------|------------|
| Quetta              | Q          | Dezi                | d          |
| Ronna               | R          | Zenti               | c          |
| Yotta               | Y          | Milli               | m          |
| Zetta               | Z          | Mikro               | &micro;    |
| Exa                 | E          | Nano                | n          |
| Peta                | P          | Piko                | p          |
| Tera                | T          | Femto               | f          |
| Giga                | G          | Atto                | a          |
| Mega                | M          | Zepto               | z          |
| Kilo                | k          | Yokto               | y          |
| Hekto               | h          | Ronto               | r          |
| Deka                | da         | Quekto              | q          |

## SI Suffix for Exponents
| __Positive Suffix__ | __Negative Suffix__ |
|---------------------|---------------------|
| &sup1;              | &#x207B;&sup1;      |
| &sup2;              | &#x207B;&sup2;      |
| &sup3;              | &#x207B;&sup3;      |

## Mathematical Operators
| __Operator__                             | __Symbol__ |
|------------------------------------------|------------|
| Center point /<br/> Multiplication point | &middot;   |
| Multiplication sign                      | &times;    |
| Asterisk                                 | *          |
| Letter x                                 | x          |
| Slash /<br/> Division sign               | &sol;      |

## Informal Prefix & Suffix 
| __Prefix__   | __Symbol__ | __Suffix__ | __Symbol__ | 
|--------------|------------|------------|------------|
| Cubic        | c          | Cubic      | 2          |
| Square (lat) | q          | Square     | 3          |

# Installation & Setup
TODO:

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

## `normalize(text: str) -> str`
TODO:

# Links
References to the sources that contributed to the content of the page, among
other things.

- https://de.wikipedia.org/wiki/Internationales_Einheitensystem
- https://de.wikipedia.org/wiki/Gebr%C3%A4uchliche_Nicht-SI-Einheiten
- https://www.taschenhirn.de/aktuelles-allgemeinwissen/liste-masseinheiten-formeln/
- https://www.tablesgenerator.com/markdown_tables
