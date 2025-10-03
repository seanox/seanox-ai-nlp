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
    DATA = auto()


def _re_compile_logic_pattern(*pattern: str) -> re.Pattern:
    return re.compile(
        rf"(?i)^({'|'.join([f'(?:{pattern})' for pattern in pattern])})$"
    )


_LANGUAGE_LOGIC_PATTERN: dict[str, dict[Type, list[re.Pattern] | None]] = {
    "de": {
        Type.AND: None,
        Type.OR: [
            re.compile("oder|sonst")
        ],
        Type.NOT: [
            _re_compile_logic_pattern(
                r"ohne",
                r"weder|noch",
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

_MODEL_DIR = os.path.join(os.getcwd(), "stanza")

_pipelines: dict[str, stanza.Pipeline] = {}


def _download_pipeline_lazy(language: str):
    if os.path.exists(os.path.join(_MODEL_DIR, language)):
        return
    stanza.download(language, model_dir=_MODEL_DIR)


_CLAUSE_RELATIONS = {"ccomp", "xcomp", "advcl", "acl", "relcl", "parataxis", "conj"}


def _get_clause_id(word: Word, sentence: Sentence) -> int | None:

    # Search for clause indicators
    current = word
    while current.head != 0:
        head = sentence.words[current.head - 1]
        if head.deprel in _CLAUSE_RELATIONS:
            return head.id
        current = head

    # Search for root word if no clause is present (because main clause)
    for word in sentence.words:
        if word.head == 0:
            return word.id

    # Special case: Nothing found
    return None


def _create_logic_chain(
        doc: stanza.Document,
        entities: list[tuple[int, int, str]],
        pattern: dict[Type, list[re.Pattern]]
) -> list[tuple[Type, Optional[dict[str, Any]]]]:

    if not entities:
        return []

    entities = {
        start: {"start": start, "end": end, "label": label}
        for start, end, label in entities
    }

    structures: dict[int | None, list] = {}
    for sentence in doc.sentences:
        for word in sentence.words:
            if word.start_char in entities:
                clause = _get_clause_id(word, sentence)
                if clause not in structures:
                    structures[clause] = []
                entity = entities[word.start_char]
                entity["word"] = word
                entity["clause"] = _get_clause_id(word, sentence)
                structures[clause].append(entity)

    return []


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
