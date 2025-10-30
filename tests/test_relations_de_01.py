# tests/test_relations_de_01.py

from tests.utilities import _create_entities
from seanox_ai_nlp.relations.relations import (
    relations,
    pretty_print_node,
    sentences,
    pretty_print_sentences
)


BAKING_ENTITIES_PATTERN = [
    ("FRUITS", r"(?i)\bÄpfel|Birnen|Kirschen|Pflaumen|Erdbeeren\b"),
    ("TREATS", r"(?i)\bObstkuchen|Plätzchen|Dessert\b"),
    ("INGREDIENTS", r"(?i)\bSchokolade|Zucker|Mehl|Eier\b"),
    ("TERM", r"(?i)\bZutaten\b")
]

EXAMPLES_TEXT_01 = [
    "Hole Äpfel für den Obstkuchen, Schokolade für die Plätzchen aber keine Erdbeeren.",
    "Hole Äpfel und Birnen für den Obstkuchen, Schokolade für die Plätzchen aber keine Erdbeeren.",
    "Hole Äpfel, Pflaumen und Birnen für den Obstkuchen, Schokolade für die Plätzchen aber keine Erdbeeren.",
    "Hole keine Äpfel und Pflaumen, aber Birnen für den Obstkuchen, Schokolade für die Plätzchen und keine Erdbeeren.",
    "Gibt es ein Dessert ohne Äpfel, Schokolade oder Erdbeeren?",

    "Hole keine Äpfel, Pflaumen oder Birnen aber Erdbeeren.",
    "Hole keine Äpfel, Pflaumen oder Birnen, sondern Erdbeeren.",

    "Hole Äpfel, keine Pflaumen oder Birnen aber Erdbeeren.",
    "Hole Äpfel und Erdbeeren, aber keine Pflaumen oder Birnen.",

    "Hole Äpfel, keine Pflaumen und Birnen aber Erdbeeren."
    "Hole Äpfel und Erdbeeren, aber keine Pflaumen und keine Birnen.",

    "Das Mehl brauche ich für den Kuchen und ich brauche es für die Plätzchen.",
    "Ich brauche keine Kirschen aber Äpfel.",
    "Hole keine Äpfel, jedoch Birnen.",
    "Hole Äpfel, jedoch keine Birnen."
]


def test_logics_03():

    # TODO:
    text = EXAMPLES_TEXT_01[2]
    pretty_print_sentences(sentences("de", text))

    entities = _create_entities(text, BAKING_ENTITIES_PATTERN)
    entities = [(ent["start"], ent["end"], ent["label"]) for ent in entities]
    print(entities)

    node = relations("de", text, entities)
    print(node)
    pretty_print_node(node)

# Text: "Get apples for the fruit cake, chocolate for the cookies, but no strawberries."
# Entities: [
#    {"label": "FRUITS", "text": "apples", "start": 4, "end": 10},
#    {"label": "TREATS", "text": "fruit cake", "start": 19, "end": 29},
#    {"label": "INGREDIENTS", "text": "chocolate", "start": 31, "end": 40},
#    {"label": "TREATS", "text": "cookies", "start": 49, "end": 56},
#    {"label": "FRUITS", "text": "strawberries", "start": 65, "end": 77}
#]

# SET
# +- ENTITY (label:FRUITS, text:apples)
# +- ENTITY (label:TREATS, text:fruit cake)
# |  +- ENTITY (label:INGREDIENTS, text:chocolate)
# |  +- ENTITY (label:TREATS, text:cookies)
# +- NOT
#    +- ENTITY DATA (label:FRUITS, text:strawberries)

# Relations in an ENTITY are UNION
# A set of elements in a branch without a direct ENTITY as parent are SET
