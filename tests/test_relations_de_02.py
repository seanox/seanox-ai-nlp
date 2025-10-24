# tests/test_relations_de_02.py

from tests.utilities import _create_entities
from seanox_ai_nlp.relations.relations import (
    relations,
    pretty_print_node,
    sentences,
    pretty_print_sentences
)


EXAMPLE_ENTITIES_PATTERN = [
    ("PERSONS", r"(?i)\bPeter|Paul\b"),
    ("VEHICLES", r"(?i)\bAuto|Fahrrad\b"),
    ("TERM", r"(?i)\bGeld\b"),
]

EXAMPLES_TEXT_01 = [
    "Nicht Peter, sondern Paul hat kein Auto und kein Fahrrad, weil er kein Geld hat."
]


def test_logics_01():

    text = EXAMPLES_TEXT_01[0]
    pretty_print_sentences(sentences("de", text))

    entities = _create_entities(text, EXAMPLE_ENTITIES_PATTERN)
    entities = [(ent["start"], ent["end"], ent["label"]) for ent in entities]
    print(entities)

    node = relations("de", text, entities)
    print(node)
    pretty_print_node(node)
