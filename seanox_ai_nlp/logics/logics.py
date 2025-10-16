# seanox_ai_npl/logics/logics.py

from enum import Enum, auto
from stanza.models.common.doc import Word, Sentence
from typing import Optional, Callable, Union, NamedTuple

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

    nodes = {0: []}
    for word in sentence.words:
        nodes.setdefault(word.id, [])
        nodes.setdefault(word.head, []).append(word.id)

    def recurse(node_id: int, prefix: str = "", is_last: bool = True, is_root: bool = False):
        word = sentence.words[node_id - 1]
        label = f"{word.text} (id:{word.id}, head:{word.head}, lemma:{word.lemma}, upos:{word.upos}, deprel:{word.deprel}, feats:{word.feats})"
        connector = "" if is_root else ("└─ " if is_last else "├─ ")
        print(prefix + connector + label)

        # Only expand if a connector has been set
        prefix = prefix if is_root else prefix + ("   " if is_last else "│  ")
        for index, child_id in enumerate(nodes.get(node_id, [])):
            recurse(child_id, prefix, index == len(nodes[node_id]) - 1)

    # Start directly with the node of ROOT (id 0),
    # without connector and without indentation
    root_nodes = nodes.get(0, [])
    for index, root_node_id in enumerate(root_nodes):
        recurse(root_node_id, "", index == len(root_nodes) - 1, is_root=True)


def _get_word_feats(word: Word) -> dict[str, str]:
    if not word or not word.feats:
        return {}
    return dict(feat.split("=", 1) for feat in word.feats.split("|"))


def _get_logical_relations(sentence: Sentence, word: Word) -> set[Type]:

    relations: set[Type] = set()

    # Only entities are considered
    if not word.entity:
        return relations

    for child in sentence.words:
        if child.head != word.id:
            continue
        if child.deprel == "neg":
            relations.add(Type.NOT)
        if child.feats:
            feats = _get_word_feats(child)
            if "Polarity" in feats and feats["Polarity"] == "Neg":
                relations.add(Type.NOT)
            if "PronType" in feats and feats["PronType"] == "Neg":
                relations.add(Type.NOT)
            if "Negative" in feats and feats["Negative"] == "Neg":
                relations.add(Type.NOT)
    if word.deprel == "neg":
        relations.add(Type.NOT)

    # Without anything, but others entities refer to it, it will be ANY
    if not relations:
        heads = {
            item.head
            for item in sentence.words
            if item.entity
        }
        if word.id in heads:
            relations.add(Type.ANY)

    # Without anything else, it will be ANY
    if not relations:
        relations.add(Type.DATA)

    return relations


def _get_word_path(sentence, word) -> list[int]:
    path: list[int] = []
    while True:
        path.insert(0, word.head)
        if word.head <= 0:
            break
        word = sentence.words[word.head - 1]
    return path


class Entity(NamedTuple):
    start: int
    end: int
    label: str
    text: str


Data = tuple[Type, Entity]
Tree = tuple[Type, Optional[list["Node"]]]
Node = Union[Data, Tree]


def _print_structure_tree(node: Node):

    def recurse(node: Node, prefix: str = "", is_root: bool = True):

        typ, tree = node
        if not tree:
            return

        # The type is only output here for the root node.
        # For recursive calls (is_root=False), the type was already
        # output in the previous print().
        if is_root:
            print(typ.name)

        for index, node in enumerate(tree):

            is_last = index == len(tree) - 1
            branch = "└─ " if is_last else "├─ "
            node_prefix = prefix + ("   " if is_last else "│  ")

            type, entity = node
            if type == Type.DATA:
                print(prefix + branch + f"{type.name} (label:{entity.label}, text:{entity.text})")
            else:
                print(prefix + branch + type.name)
                recurse(node, node_prefix, is_root=False)

    recurse(node)


# Retrieval-Union Semantics (RUS)
# Everything mentioned is retrieved by default (union / ANY). OR does not need
# to be explicitly modeled, since enumerations are always interpreted as unions.
# NOT is used for exclusion. An explicit AND in the sense of an intersection
# does not exist -- sounds too simple, but it's all about combinatorics,
# nesting, and normalization.

def _create_structure_tree(structure: dict[int, tuple[list[int], Word]]) -> Node:

    words: dict[int, list[int]] = {id: [] for id in structure}

    roots = [word for id, (path, word) in structure.items() if path == [0]]
    if not roots:
        roots = [word for id, (path, word) in structure.items()
                 if len(path) == 2 and path[0] == 0]

    for id, (path, word) in structure.items():
        if word not in roots:
            parent = path[-1]
            if parent in words and parent != id:
                words[parent].append(id)

    def create_node(word: Word) -> Node:
        type = next(iter(word.types))
        if Type.DATA == type:
            return (type, word.entity if word.entity else None)
        tree: Tree = [(Type.DATA, word.entity)]
        for id in words.get(word.id, []):
            tree.append(create_node(structure[id][1]))
        return (type, tree if tree else None)

    if not roots:
        return (Type.ANY, None)
    tree = [create_node(root) for root in roots]
    if len(tree) == 1:
        return tree[0]
    return (Type.ANY, tree)


def _create_logic_chain(
        doc: stanza.Document,
        entities: list[tuple[int, int, str]],
        patterns: dict[Type, list[re.Pattern]]
) -> Node:

    if not entities:
        return (Type.ANY, None)

    # TODO: Multi-Word / Multi-Token Entities
    # TODO: Entities refer to the entire text with start and end, e.g. beyond sentences

    # Dictionary with the starting positions of the entities
    entities = {entity.start: entity for entity in entities}

    for sentence in doc.sentences:
        # 1. Injection of additional attributes
        for word in sentence.words:
            word.path = _get_word_path(sentence, word)
            word.types = set()
            # ignore MWT (Multi-Word Token without start_char)
            if word.start_char is not None and word.start_char in entities:
                word.entity = entities[word.start_char]

        # 2. Tagging logical relations only for entities
        for word in sentence.words:
            # ignore MWT (Multi-Word Token without start_char)
            if word.entity:
                logic_relations = _get_logical_relations(sentence, word)
                if logic_relations:
                    word.types.update(logic_relations)

        # 3. Creating a flat tree structure of only the relevant entities
        structure = {word.id: (word.path, word) for word in sentence.words if word.types}

        # X. Normalize paths
        # - shorten each path by removing nodes not present in flat
        # - only keep parent IDs that are valid keys in flat
        # - and keep 0 as an indicator for ROOT so that paths are never empty
        heads = set(structure.keys())
        for id, (path, word) in structure.items():
            structure[id] = ([head for head in path if head == 0 or head in heads], word)

        # TODO:
        _print_sentence_tree(sentence)
        _print_structure_tree(_create_structure_tree(structure))

    return (Type.ANY, None)


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


def logics(language: str, text: str, entities: list[tuple[int, int, str]]) -> Node:

    language = (language or "").strip()
    if not language:
        raise ValueError("Language is required")
    if language.lower() not in set(_LANGUAGE_LOGIC_PATTERN.keys()):
        raise ValueError(f"Language '{language}' is not supported")
    language = language.lower()

    if not text.strip() or not entities:
        return (Type.ANY, None)

    mapping = _LANGUAGE_SENTENCE_MAPPING.get(language)
    if mapping is not None:

        # First pass as a preprocess to change everyday logical words and
        # phrases in Universal Dependencies words and phrases so that the stanza
        # pipelines can interpret them.
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

    entities = [
        Entity(start, end, label, text[start:end])
        for start, end, label in entities
    ]

    return _create_logic_chain(doc, entities, _LANGUAGE_LOGIC_PATTERN[language])
