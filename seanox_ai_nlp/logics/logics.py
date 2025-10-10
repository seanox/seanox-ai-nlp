# seanox_ai_npl/logics/logics.py

from enum import Enum, auto
from stanza.models.common.doc import Word, Sentence
from typing import Optional, Callable

import os
import re
import stanza

_MODEL_DIR = os.path.join(os.getcwd(), ".stanza")


class Type(Enum):
    ANY = auto()
    NOT = auto()
    INVERT = auto()
    DATA = auto()


def _re_compile_logic_pattern(*pattern: str) -> re.Pattern:
    return re.compile(
        rf"(?i)^({'|'.join([f'(?:{pattern})' for pattern in pattern])})$"
    )


_LANGUAGE_SENTENCE_MAPPING: dict[str, Callable[[Sentence], list[str]]] | None = {
    "de": None,
    "dk": None,
    "en": None,
    "es": None,
    "fr": None,
    "it": None,
    "ru": None
}

_LANGUAGE_LOGIC_PATTERN: dict[str, dict[Type, list[re.Pattern] | None]] = {

    # https://universaldependencies.org/docs/en/dep/neg.html
    # https://universaldependencies.org/de/
    # nicht / nichts / nicht einmal / nicht mehr / nicht mal / noch nicht
    # kein / keine / keiner / keines
    # nie / niemals
    # ohne, weder (noch)

    "de": {
        Type.ANY: None,
        Type.NOT: [
            _re_compile_logic_pattern(
                r"ohne|weder|noch",
                r"nie(mals)?",
                r"nicht(s)?",
                r"kein(e|s|((er|es)[a-z]*))?",
                r"ausge(nommen|schlossen)"
            )
        ],
        Type.INVERT: [
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


_pipelines: dict[str, stanza.Pipeline] = {}


def _download_pipeline_lazy(language: str):
    if os.path.exists(os.path.join(_MODEL_DIR, language)):
        return
    stanza.download(language, model_dir=_MODEL_DIR)


def _get_related_entities(sentence: Sentence, word: Word, entities: dict[int, dict]) -> list[dict] | None:
    return []


Node = tuple[Type, Optional["Tree"]]
Tree = list[Node]


# Retrieval-Union Semantics (RUS)
# Everything mentioned is retrieved by default (union / ANY). OR does not need
# to be explicitly modeled, since enumerations are always interpreted as unions.
# NOT is used for exclusion. An explicit AND in the sense of an intersection
# does not exist -- sounds too simple, but it's all about combinatorics,
# nesting, and normalization.

def _create_logic_chain(
        doc: stanza.Document,
        entities: list[tuple[int, int, str]],
        patterns: dict[Type, list[re.Pattern]]
) -> Tree:

    if not entities:
        return []

    for sentence_id, sentence in enumerate(doc.sentences):
        words = []
        for word in sentence.words:
            print(word)


    return []


def _get_pipeline(language: str, processors: str | None) -> stanza.Pipeline:

    if not processors or not processors.strip():
        processors = "tokenize,mwt,pos,lemma,depparse"

    # stanza usually requires the tokenize processor for its pipelines. Since
    # the list of processors is checked before tokenize_pretokenized is
    # evaluated, tokenize must always be specified to ensure that dependencies
    # are met. However, in cases where the text is already pre-segmented, this
    # would distort the logic of the processor list. Therefore, tokenize is
    # automatically added here if it is missing, and the tokenize_pretokenized
    # option is set depending on the actual existence of tokenize.

    processors = [
        processor.strip().lower()
        for processor in processors.split(",")
        if processor.strip()
    ]
    tokenizer = "tokenize" in processors
    if not tokenizer:
        processors.insert(0, "tokenize")
    processors = ",".join(processors)

    signature = (language, processors)
    if signature not in _pipelines:
        _download_pipeline_lazy(language)
        _pipelines[signature] = stanza.Pipeline(
            lang=language,
            processors=processors,
            tokenize_pretokenized=not tokenizer,
            model_dir=_MODEL_DIR,
            download_method=None,
            use_gpu=False
        )
    return _pipelines[signature]


def logics(language: str, text: str, entities: list[tuple[int, int, str]]) -> Tree:

    language = (language or "").strip()
    if not language:
        raise ValueError("Language is required")
    if language.lower() not in set(_LANGUAGE_LOGIC_PATTERN.keys()):
        raise ValueError(f"Language '{language}' is not supported")
    language = language.lower()

    if not text.strip() or not entities:
        return Tree()

    mapping = _LANGUAGE_SENTENCE_MAPPING.get(language)
    if mapping is not None:

        # First pass as a preprocess to change everyday logical words and phrases in
        # Universal Dependencies words and phrases so that the stanza pipelines can
        # interpret them.
        nlp = _get_pipeline(language, processors="tokenize,mwt")
        doc = nlp(text)
        sentences = []
        for sentence in doc.sentences:
            sentences.append(mapping(sentence))

        # Second pass to determine the actual logical structure.
        nlp = _get_pipeline(language, processors="pos,lemma,depparse")
        doc = nlp(sentences)
    else:
        nlp = _get_pipeline(language, processors="tokenize,mwt,pos,lemma,depparse")
        doc = nlp(text)

    return _create_logic_chain(doc, entities, _LANGUAGE_LOGIC_PATTERN[language])
