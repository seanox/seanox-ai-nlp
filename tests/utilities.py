# tests/utilities.py

import json
import os
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


def _pretty_entities(text, ents):
    entities = []
    for start, end, label in ents:
        entity_text = text[start:end]
        entities.append({
            "label": label,
            "text": entity_text,
            "start": start,
            "end": end
        })
    dumps = f",{os.linesep}  ".join(
        json.dumps(entity, ensure_ascii=False)
        for entity in entities
    )
    return f"[{os.linesep}  {dumps}{os.linesep}]"
