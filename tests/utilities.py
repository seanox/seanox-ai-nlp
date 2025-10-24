# tests/utilities.py

import re


def _create_entities(text: str, patterns: list[tuple[str, str]]) -> list[dict]:
    entities = []
    for label, pattern in patterns:
        for match in re.finditer(pattern, text):
            entities.append({
                "text": match.group(),
                "start": match.start(),
                "end": match.end(),
                "label": label
            })
    return entities
