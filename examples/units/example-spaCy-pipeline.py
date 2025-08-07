# examples/units/example-spaCy-pipeline.py
# Run: python -m spacy download en_core_web_md
#      python examples/units/example-spaCy-pipeline.py

import spacy
from spacy.tokens import Span
from seanox_ai_nlp.units import units

Span.set_extension("value", default=None)
Span.set_extension("unit", default=None)
Span.set_extension("categories", default=None)

# Loading model and text
nlp = spacy.load("en_core_web_md")
text = (
    "The cruising speed of the Boeing 747 is approximately 900 - 950 km/h (559 mph)."
    "It is typically expressed in kilometers per hour (km/h) and miles per hour (mph)."
)
doc = nlp(text)

# Detecting entities in text
units_entites = units(text)
for units_entity in units_entites:
    span = doc.char_span(
        units_entity.start,
        units_entity.end,
        label=units_entity.label
    )
    if span:
        # Enrichment of the spans
        span._.value = units_entity.value
        span._.unit = units_entity.unit
        span._.categories = list(units_entity.categories)
        doc.ents += (span,)

# Formatted output
for ent in doc.ents:
    if ent.label_ in ["UNIT", "UNIT-VALUE"]:
        print(f"{ent.text:<20} | label: {ent.label_:<10} | value: {ent._.value or '':<10} | unit: {ent._.unit:<6} | categories: {ent._.categories}")
    else:
        print(f"{ent.text:<20} | label: {ent.label_}")

# Output:
# Boeing               | label: ORG
# 747                  | label: PRODUCT
# 900 - 950 km/h       | label: UNIT-VALUE | value: 900 - 950  | unit: km/h   | categories: ['length', 'time']
# 559                  | label: CARDINAL
# in                   | label: UNIT       | value:            | unit: in     | categories: ['length']
# kilometers per hour  | label: TIME
# km/h                 | label: UNIT       | value:            | unit: km/h   | categories: ['length', 'time']
# mph                  | label: UNIT       | value:            | unit: mph    | categories: ['length']
