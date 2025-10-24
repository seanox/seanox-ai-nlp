# tests/test_relations_de_01.py

from tests.utilities import _create_entities
from seanox_ai_nlp.relations.relations import (
    relations,
    pretty_print_node,
    sentences,
    pretty_print_sentences
)


BAKING_ENTITIES_PATTERN = [
    ("FRUITS", r"(?i)\bÄpfel|Birnen|Pflaumen|Erdbeeren\b"),
    ("TREATS", r"(?i)\bObstkuchen|Plätzchen|Dessert\b"),
    ("INGREDIENTS", r"(?i)\bSchokolade\b"),
    ("TERM", r"(?i)\bZutaten\b"),

    ("FRUITS", r"(?i)\bapples|pears|plums|strawberries\b"),
    ("TREATS", r"(?i)\bfruit cake|cookies|dessert\b"),
    ("INGREDIENTS", r"(?i)\bchocolate\b"),
    ("TERM", r"(?i)\bingredients\b")
]

EXAMPLES_TEXT_01 = [
    "Hole Äpfel für den Obstkuchen, Schokolade für die Plätzchen aber keine Erdbeeren.",
    "Hole Äpfel und Birnen für den Obstkuchen, Schokolade für die Plätzchen aber keine Erdbeeren.",
    "Hole Äpfel, Pflaumen und Birnen für den Obstkuchen, Schokolade für die Plätzchen aber keine Erdbeeren.",
    "Hole keine Äpfel und Pflaumen, aber Birnen für den Obstkuchen, Schokolade für die Plätzchen und keine Erdbeeren.",
    "Gibt es ein Dessert ohne Äpfel, Schokolade oder Erdbeeren?"
]


def test_logics_03():

    text = EXAMPLES_TEXT_01[2]
    pretty_print_sentences(sentences("de", text))

    #entities = _create_entities(text, BAKING_ENTITIES_PATTERN)
    #entities = [(ent["start"], ent["end"], ent["label"]) for ent in entities]
    # print(entities)

    #node = relations("de", text, entities)
    #print(node)
    #pretty_print_node(node)
