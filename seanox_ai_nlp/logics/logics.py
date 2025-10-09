# seanox_ai_npl/logics/logics.py

from enum import Enum, auto
from stanza.models.common.doc import Word, Sentence
from typing import Optional, Any

import os
import re
import stanza


class Type(Enum):
    AND = auto()
    OR = auto()
    NOT = auto()
    INV = auto()
    GROUP = auto()
    DATA = auto()


def _re_compile_logic_pattern(*pattern: str) -> re.Pattern:
    return re.compile(
        rf"(?i)^({'|'.join([f'(?:{pattern})' for pattern in pattern])})$"
    )


_LANGUAGE_LOGIC_PATTERN: dict[str, dict[Type, list[re.Pattern] | None]] = {
    "de": {
        Type.AND: None,
        Type.OR: [
            _re_compile_logic_pattern(
                r"oder|sonst"
            )
        ],
        Type.NOT: [
            _re_compile_logic_pattern(
                r"ohne|weder|noch",
                r"nie(mals)?",
                r"nicht",
                r"kein(e|s|((er|es)[a-z]*))?",
                r"ausge(nommen|schlossen)"
            )
        ],
        Type.INV: [
            None
        ]
    },
#   "dk": {
#   },
#   "en": {
#   },
#   "es": {
#   },
#   "fr": {
#   },
#   "it": {
#   },
#   "ru": {
#   }
}

_MODEL_DIR = os.path.join(os.getcwd(), ".stanza")

_pipelines: dict[str, stanza.Pipeline] = {}


def _download_pipeline_lazy(language: str):
    if os.path.exists(os.path.join(_MODEL_DIR, language)):
        return
    stanza.download(language, model_dir=_MODEL_DIR)


_CLAUSE_RELATIONS = {"ccomp", "xcomp", "advcl", "acl", "relcl", "parataxis", "conj"}


def _get_clause_id(sentence: Sentence, word: Word) -> int | None:

    # Search for clause indicators
    current = word
    while current.head != 0:
        if current.deprel in _CLAUSE_RELATIONS:
            return current.id
        current = sentence.words[current.head - 1]

    # Search for root word if no clause is present (because main clause)
    for word in sentence.words:
        if word.head == 0:
            return word.id

    # Special case: Nothing found
    return None


def _get_related_entity(sentence: Sentence, word: Word, entities: dict[int, dict]) -> dict | None:
    while True:
        if word.id in entities.keys():
            return entities.get(word.id)
        if word.head == 0:
            break
        word = sentence.words[word.head - 1]
    return None


def _create_logic_chain(
        doc: stanza.Document,
        entities: list[tuple[int, int, str]],
        patterns: dict[Type, list[re.Pattern]]
) -> list[tuple[Type, dict[str, Any] | None | list]]:

    if not entities:
        return []

    # New dictionary with the starting positions
    entities_starts = {
        start: {"start": start, "end": end, "label": label}
        for start, end, label in entities
    }

    structures: dict[int | None, list] = {}
    for sentence in doc.sentences:
        for word in sentence.words:
            if word.start_char in entities_starts:
                clause = _get_clause_id(sentence, word)
                if clause not in structures:
                    structures[clause] = []
                entity = entities_starts[word.start_char]
                entity["clause"] = clause
                entity["word"] = word
                structures[clause].append((Type.DATA, entity))

    # New dictionary with word IDs of the entities
    entity_index = {
        entity["word"].id: entity
        for clause in structures.values()
        for type, entity in clause
    }

    # Second pass: Identify logical operators and insert them before entities,
    # since logical words can also occur semantically after an entity, but must
    # be entered logically before the entity.
    for sentence in doc.sentences:
        for word in sentence.words:
            for operator, pattern in patterns.items():
                if not pattern:
                    continue
                for regex in pattern:
                    if not regex or not regex.match(word.lemma):
                        continue
                    entity = _get_related_entity(sentence, word, entity_index)
                    if entity:
                        structure = structures[entity["clause"]]
                        structure.insert(structure.index((Type.DATA, entity)), (operator, None))
                    # Because these are logical flags with no fixed order (which
                    # is also true for AND and OR, but reads strangely), each
                    # match can be inserted before the entity -- without a break

    # Assemble final structure
    # All groups and entities that are not related by a logical operator are
    # related by AND, based on the assumption that all entities of the input are
    # related in context and are therefore implicitly related by AND.
    structures_result = []
    for structures_index, structure in enumerate(structures.values()):
        if structures_index > 0:
            structures_result.append((Type.AND, None))
        structure_result = []
        for structure_index, (type, entity) in enumerate(structure):
            if Type.DATA == type:
                if structure_index > 0 and Type.DATA == structure[structure_index - 1][0]:
                    structure_result.append((Type.AND, None))
                structure_result.append((
                    Type.DATA,
                    {
                        "start": entity["start"],
                        "end": entity["end"],
                        "label": entity["label"],
                        "value": entity["word"].text
                    }
                ))
            else:
                structure_result.append((type, entity))
        structures_result.append((Type.GROUP, structure_result))

    return structures_result


def _get_pipeline(language: str) -> stanza.Pipeline:
    if language not in _pipelines:
        _download_pipeline_lazy(language)
        _pipelines[language] = stanza.Pipeline(
            lang=language,
            processors="tokenize,mwt,pos,lemma,depparse",
            model_dir=_MODEL_DIR,
            download_method=None,
            use_gpu=False
        )
    return _pipelines[language]


def logics(
        language: str,
        text: str,
        entities: list[tuple[int, int, str]]
) -> list[tuple[Type, Optional[dict[str, Any]]]]:

    language = (language or "").strip()
    if not language:
        raise ValueError("Language is required")
    if language.lower() not in set(_LANGUAGE_LOGIC_PATTERN.keys()):
        raise ValueError(f"Language '{language}' is not supported")
    language = language.lower()

    if not text.strip() or not entities:
        return []

    nlp = _get_pipeline(language)
    doc = nlp(text)
    return _create_logic_chain(doc, entities, _LANGUAGE_LOGIC_PATTERN[language])
