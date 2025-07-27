## Description
TODO:

This list contains common language-independent base units as they typically
appear in natural sentences -- ranging from everyday usage to slightly technical
or mildly academic contexts. The columns __Informal Prefix__ and __Informal
Suffix__ take into account additional forms that may occur in informal or
non-standard contexts.

The table serves:
- as an overview of supported units of measurement,
- as a basis for creating regular expressions (RegEx) to identify units as
  phrases in texts.

## Units
__Note__ These are base units only. Variants result from the additional
properties recorded. There is no claim to interpretation, classification, or
complete standardization of the units (e.g., [IEC](https://iec.ch/si),
[BIPM][https://www.bipm.org/en/measurement-units]).

| Unit                    | __Symbol__    | SI conform | Exponents | Informal Prefix | Informal Suffix |
|-------------------------|---------------|------------|-----------|-----------------|-----------------|
| Degree                  | __&ordm;__    |            |           |                 |                 |
| Degree Celsius          | __&ordm;C__   |            |           |                 |                 |
| Minute                  | __&#x2032;__  |            |           |                 |                 |
| Second                  | __&#x2033;__  |            |           |                 |                 |
| Inch (quote mark)       | __&#x2033;__  |            | x         |                 |                 |
| Astronomical Unit       | __AE__        |            |           |                 |                 |
| Ampere                  | __A__         | x          | x         |                 |                 |
| Atmosphere (pressure)   | __atm__       |            |           |                 |                 |
| Gauge Pressure (Atü)    | __Atü__       |            |           |                 |                 |
| Are                     | __a__         |            | x         | x               | x               |
| Acceleration            | __a__         |            |           |                 |                 |
| Year                    | __a__         |            |           |                 |                 |
| Bar                     | __bar__       | x          |           |                 |                 |
| Barrel (oil)            | __bbl__       |            |           |                 |                 |
| Becquerel               | __Bq__        | x          |           |                 |                 |
| Coulomb                 | __C__         | x          | x         |                 |                 |
| Candela                 | __cd__        | x          |           |                 |                 |
| Carat (gem weight)      | __ct__        |            |           |                 |                 |
| Day                     | __d__         | x          |           |                 |                 |
| Dekameter               | __dam__       | x          | x         |                 |                 |
| Decibel                 | __dB__        |            |           |                 |                 |
| Dioptre                 | __dpt__       |            |           |                 |                 |
| Double Hundredweight    | __dz__        |            |           |                 |                 |
| Dozen                   | __Dz__        |            |           |                 |                 |
| Farad                   | __F__         | x          | x         |                 |                 |
| Foot                    | __ft__        |            | x         | x               | x               |
| Gallon                  | __gal__       |            |           |                 |                 |
| Gram                    | __g__         | x          |           |                 |                 |
| Henry                   | __H__         | x          | x         |                 |                 |
| Hour                    | __h__         |            |           |                 |                 |
| Hectare                 | __ha__        |            | x         | x               | x               |
| Hectoliter              | __hl__        |            |           |                 |                 |
| Horsepower (imperial)   | __hp__        |            |           |                 |                 |
| Hertz                   | __Hz__        | x          |           |                 |                 |
| Inch                    | __in__        |            | x         | x               | x               |
| Joule                   | __J__         | x          | x         |                 |                 |
| Kelvin                  | __K__         | x          | x         |                 |                 |
| Karat (gold purity)     | __kt__        |            |           |                 |                 |
| Liter                   | __l__         | x          |           |                 |                 |
| Light-year              | __lj__        |            | x         |                 |                 |
| Lumen                   | __lm__        | x          |           |                 |                 |
| Lumen second            | __ls__        |            |           |                 |                 |
| Lux                     | __lx__        | x          |           |                 |                 |
| Meter                   | __m__         | x          | x         | x               | x               |
| Mile                    | __mi__        |            | x         | x               | x               |
| Minute (long form)      | __min__       |            |           |                 |                 |
| Mole                    | __mol__       | x          |           |                 |                 |
| Newton                  | __N__         | x          |           |                 |                 |
| Ohm                     | __?__         | x          | x         |                 |                 |
| Ounce                   | __oz.__       |            |           |                 |                 |
| Troy Ounce              | __oz.tr.__    |            |           |                 |                 |
| Pascal                  | __Pa__        | x          |           |                 |                 |
| Parsec                  | __pc__        |            | x         | x               | x               |
| Pound                   | __Pf__        |            |           |                 |                 |
| Pond (metric force)     | __p__         | x          |           |                 |                 |
| Horsepower (metric)     | __PS__        |            |           |                 |                 |
| Pint                    | __pt__        |            |           |                 |                 |
| Radian                  | __rad__       | x          |           |                 |                 |
| Cubic meter (Raummeter) | __rm__        |            | x         | x               | x               |
| Second (long form)      | __s__         | x          | x         |                 |                 |
| Siemens                 | __S__         | x          |           |                 |                 |
| Square foot             | __sq.ft.__    |            |           |                 |                 |
| Square inch             | __sq.in.__    |            |           |                 |                 |
| Square mile             | __sq.mile__   |            |           |                 |                 |
| Square yard             | __sq.yd.__    |            |           |                 |                 |
| Steradian               | __sr__        | x          |           |                 |                 |
| Stere (wood volume)     | __St__        |            | x         | x               | x               |
| Tesla                   | __T__         | x          | x         |                 |                 |
| Tonne                   | __t__         | x          |           |                 |                 |
| Atomic Mass Unit        | __u__         |            |           |                 |                 |
| Velocity                | __v__         |            | x         |                 | x               |
| Volt                    | __V__         | x          | x         |                 | x               |
| Watt                    | __w__         | x          |           |                 |                 |
| Weber                   | __Wb__        | x          |           |                 |                 |
| Yard                    | __yd__        |            | x         | x               | x               |
| Zentner (100kg)         | __Z__         |            |           |                 |                 |
| Density                 | __&rho;__     |            |           |                 |                 |
| Angular Frequency       | __&omega;__   |            | x         |                 | x               |

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
| Slash /<br/> Division sign               | &sol;      |

## Informal Prefix & Suffix 
| __Prefix__  | __Symbol__ | __Suffix__ | __Symbol__ | 
|-------------|------------|------------|------------|
| Cubic       | q          | Cubic      | 2          |
| Square (de) | q          | Square     | 3          |
| Square (en) | sq         |            |            |
