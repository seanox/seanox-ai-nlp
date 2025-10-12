# seanox_ai_npl/logics/logics.py

from enum import Enum, auto
from stanza.models.common.doc import Word, Sentence
from typing import Optional, Callable

import os
import re
import stanza


class Type(Enum):
    ANY = auto()
    NOT = auto()
    INVERT = auto()
    DATA = auto()


# Additional attributes for the logical structure are added to the stanza word.

Word.add_property(
    "types",
    default=None,
    getter=lambda self: getattr(self, "_types", set()),
    setter=lambda self, value: setattr(self, "_types", value)
)

Word.add_property(
    "path",
    default=None,
    getter=lambda self: getattr(self, "_path", []),
    setter=lambda self, value: setattr(self, "_path", value)
)

Word.add_property(
    "entity",
    default=None,
    getter=lambda self: getattr(self, "_entity", None),
    setter=lambda self, value: setattr(self, "_entity", value)
)


def _re_compile_logic_pattern(*pattern: str) -> re.Pattern:
    return re.compile(
        rf"(?i)^({'|'.join([f'(?:{pattern})' for pattern in pattern])})$"
    )


_LANGUAGE_SENTENCE_MAPPING: dict[str, Optional[Callable[[Sentence], list[str]]]] = {
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


def _print_sentence_tree(sentence: Sentence):

    children = {0: []}
    for word in sentence.words:
        children.setdefault(word.id, [])
        children.setdefault(word.head, []).append(word.id)

    def recurse(node_id: int, prefix: str = "", is_last: bool = True, is_root: bool = False):
        word = sentence.words[node_id - 1]
        label = f"{word.head} {word.text} (id:{word.id}, upos:{word.upos}, deprel:{word.deprel}, feats:{word.feats})"
        connector = "" if is_root else ("└─ " if is_last else "├─ ")
        print(prefix + connector + label)

        # Only expand if a connector has been set
        prefix = prefix if is_root else prefix + ("   " if is_last else "│  ")
        for index, child_id in enumerate(children.get(node_id, [])):
            recurse(child_id, prefix, index == len(children[node_id]) - 1)

    # Start directly with the children of ROOT (id 0),
    # without connector and without indentation
    root_children = children.get(0, [])
    for index, child_id in enumerate(root_children):
        recurse(child_id, "", index == len(root_children) - 1, is_root=True)


# Retrieval-Union Semantics (RUS)
# Everything mentioned is retrieved by default (union / ANY). OR does not need
# to be explicitly modeled, since enumerations are always interpreted as unions.
# NOT is used for exclusion. An explicit AND in the sense of an intersection
# does not exist -- sounds too simple, but it's all about combinatorics,
# nesting, and normalization.

def _get_logical_relations(sentence: Sentence, word: Word) -> set[Type]:

    relations = set()
    return relations


def _get_word_path(word: Word) -> list[str]:
    pass


Node = tuple[Type, Optional["Tree"]]
Tree = list[Node]


def _print_structure_tree(structure: Tree):
    pass


def _create_logic_chain(
        doc: stanza.Document,
        entities: list[tuple[int, int, str]],
        patterns: dict[Type, list[re.Pattern]]
) -> Tree:

    if not entities:
        return []

    # Dictionary with the starting positions of the entities
    entities_starts = {
        start: {"start": start, "end": end, "label": label}
        for start, end, label in entities
    }

    for sentence in doc.sentences:
        # TODO:
        _print_sentence_tree(sentence)
        # 1. Tagging of entities and logical relations
        for word in sentence.words:
            word.types = set()
            # ignore MWT (Multi-Word Token without starts)
            word_start = word.start_char
            if word_start and word_start in entities_starts:
                word.entity = entities_starts[word_start]
                word.types.add(Type.DATA)
            logic_relations = _get_logical_relations(sentence, word)
            if logic_relations:
                word.types.update(logic_relations)
            word.path = _get_word_path(word)

        # 2. Creating a flat tree structure of only the relevant entities
        flat = dict()
        for word in sentence.words:
            # TODO:
            print(f"id:{word.id}, {word.text}, path:{word.path} types:{word.types}")

    return []


_PIPELINES_MODEL_DIR = os.path.join(os.getcwd(), ".stanza")
_PIPELINES_CACHE: dict[tuple[str, str], stanza.Pipeline] = {}


def _download_pipeline_lazy(language: str):
    if os.path.exists(os.path.join(_PIPELINES_MODEL_DIR, language)):
        return
    stanza.download(language, model_dir=_PIPELINES_MODEL_DIR)


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

    key = (language, processors)
    if key not in _PIPELINES_CACHE:
        _download_pipeline_lazy(language)
        _PIPELINES_CACHE[key] = stanza.Pipeline(
            lang=language,
            processors=processors,
            tokenize_pretokenized=not tokenizer,
            model_dir=_PIPELINES_MODEL_DIR,
            download_method=None,
            use_gpu=False
        )
    return _PIPELINES_CACHE[key]


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
