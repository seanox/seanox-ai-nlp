# seanox_ai_npl/relations/relations.py

from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum, auto
from stanza.models.common.doc import Word, Sentence
from typing import Optional, Callable, Union, NamedTuple

import os
import re
import stanza


class Type(Enum):
    EMPTY = auto()
    SET = auto()
    NOT = auto()
    INVERT = auto()
    ENTITY = auto()


# Custom annotation slots (properties) for entity relations.
# stanza.Word is a central object and is extended with additional meta
# information through these properties.

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
    "relation",
    default=None,
    getter=lambda self: getattr(self, "_relation", None),
    setter=lambda self, value: setattr(self, "_relation", value)
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
    "de": {
    },
    "dk": {
    },
    "en": {
    },
    "es": {
    },
    "fr": {
    },
    "it": {
    },
    "ru": {
    }
}


def _print_sentence_tree(sentence: Sentence):

    if not sentence:
        return

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
        for index, relation_id in enumerate(nodes.get(node_id, [])):
            recurse(relation_id, prefix, index == len(nodes[node_id]) - 1)

    # Start directly with the node of ROOT (id 0),
    # without connector and without indentation
    root_nodes = nodes.get(0, [])
    for index, root_node_id in enumerate(root_nodes):
        recurse(root_node_id, "", index == len(root_nodes) - 1, is_root=True)


def _get_word_feats(word: Word) -> dict[str, str]:
    if not word or not word.feats:
        return {}
    return dict(feat.split("=", 1) for feat in word.feats.split("|"))


# Abstracts:
# - unusual/ambiguous sentence structure, then do not use NOT

def _get_word_path(sentence, word) -> list[int]:
    path: list[int] = []
    while True:
        path.insert(0, word.head)
        if word.head <= 0:
            break
        word = sentence.words[word.head - 1]
    return path


def _get_word_relation_path(sentence, word) -> list[int]:
    path: list[int] = []
    while True:
        path.insert(0, word.relation)
        if word.relation <= 0:
            break
        word = sentence.words[word.relation - 1]
    return path


def _annotate_word(sentence: Sentence, word: Word):

    # Only entities are considered
    if not word.entity:
        return

    # Every entity is ENTITY
    word.types = {Type.ENTITY}

    # TODO:
    # NOT is more complex
    # - in ambiguous/contradictory cases, NOT must be omitted
    # - NOT can/must also be recognized through keywords and spread phrases
    for relation in sentence.words:
        if relation.head != word.id:
            continue
        if relation.deprel == "neg":
            word.types.add(Type.NOT)
        if relation.feats:
            feats = _get_word_feats(relation)
            if "Polarity" in feats and feats["Polarity"] == "Neg":
                word.types.add(Type.NOT)
            elif "PronType" in feats and feats["PronType"] == "Neg":
                word.types.add(Type.NOT)
            elif "Negative" in feats and feats["Negative"] == "Neg":
                word.types.add(Type.NOT)
    if word.deprel == "neg":
        word.types.add(Type.NOT)

    # TODO:
    # Relation is initially based on UD deprel head, but to correctly map UNION,
    # SET and NOT, this must be adjusted by an extended rule.
    word.relation = word.head


class Entity(NamedTuple):
    start: int
    end: int
    label: str
    text: str


@dataclass
class NodeEmpty:
    type: Type = field(init=False, default=Type.EMPTY)


@dataclass
class NodeSet:
    type: Type = field(init=False, default=Type.SET)
    relations: list[Union["NodeSet", "NodeEntity", "NodeNot"]]

    def __post_init__(self):
        if not self.relations or len(self.relations) < 2:
            raise ValueError("At least two relationships are required")


@dataclass
class NodeEntity:
    type: Type = field(init=False, default=Type.ENTITY)
    entity: Entity
    relations: Optional[list[Union["NodeSet", "NodeEntity", "NodeNot"]]] = None


@dataclass
class NodeNot:
    type: Type = field(init=False, default=Type.NOT)
    relations: list[Union["NodeSet", "NodeEntity", "NodeNot"]] = None


Node = Union[NodeEmpty, NodeSet, NodeEntity, NodeNot]


def _print_relation_tree(node: Node):

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
            if type == Type.ENTITY:
                print(prefix + branch + f"{type.name} (label:{entity.label}, text:{entity.text})")
            else:
                print(prefix + branch + type.name)
                recurse(node, node_prefix, is_root=False)

    recurse(node)


# Retrieval-Union Semantics (RUS)
#
# Interpret logic in a retrieval-oriented manner -- not as full semantic
# reasoning, and not as formal-mathematical logic.
#
# Retrieval-Union Semantics (RUS) functions as a pre-retrieval stage in the
# information retrieval pipeline. It applies only lightweight, coarse-grained
# logic based on linguistically more stable inclusion and exclusion marker --
# negators, simple verb particles, which are often detectable in a rule-based
# manner and may contribute to reducing noise. RUS thus provides a transparent,
# deterministic filtering layer that narrows the candidate set for downstream
# processes without attempting full semantic interpretation.
#
# Everything mentioned is interpreted by default as a union (ANY), so OR does
# not need to be modeled explicitly. NOT is used for exclusion, while
# intersections (AND) emerge through combinatorics, nesting, and normalization
# rather than as a separate operator. Restrictions or enity bindings (WITH) do
# not require an explicit operator either, since they are expressed implicitly
# through tree structure and nesting. This reduction to a small set of
# primitives creates a transparent, deterministic, and auditable retrieval logic
# that can be easily integrated into existing NLP pipelines.

def _create_relation_tree(structure: dict[int, tuple[list[int], Word]]) -> Node:

    class ConvergencePoint(NamedTuple):
        path: list[int]
        id: int
        head: int
        types: set[str]
        entity: Optional[str] = None

    structure = structure.copy()

    # Find convergence points (joins) in the paths that do not exist as separate
    # words in the structure. A synthetic element with type SET will later be
    # created for each of these convergence points so that the logical nesting
    # and branching below the entities is displayed correctly.
    # Convergence points are determined from right to left. As soon as an
    # existing reference point is found in structure, the search is terminated
    # because the remaining path is already covered by this reference point in
    # structure.
    heads: dict[int, list[list[int]]] = defaultdict(list)
    for id, (path, word) in structure.items():
        for index in reversed(range(len(path))):
            head = path[index]
            if head in structure:
                break
            if head > 0:
                heads[head].append(path[:index] or [head])

    for head, paths in heads.items():
        if len(paths) > 1:
            structure[head] = (
                paths[0], ConvergencePoint(path=paths[0], id=head, head=paths[0][-1], types={Type.SET})
            )

    # Normalize paths
    # - only keep parent/head IDs that are valid keys in structure
    # - and keep 0 as an indicator for ROOT so that paths are never empty
    heads = set(structure.keys())
    for id, (path, word) in structure.items():
        structure[id] = ([head for head in path if head == 0 or head in heads], word)

    # Root is determined either directly via path [0] or the shortest path
    roots = [word for id, (path, word) in structure.items() if path == [0]]
    if not roots:
        width = min(len(path) for path, word in structure.values())
        roots = [word for path, word in structure.values() if len(path) == width]

    # Reference table words:[relations IDs]
    # It serves as a reference work for directly accessing the IDs of
    # subordinate words from a word ID.
    words: dict[int, list[int]] = {id: [] for id in structure}
    for id, (path, word) in structure.items():
        if word not in roots:
            head = path[-1]
            if head in words and head != id:
                words[head].append(id)

    def create_node(object: Word | ConvergencePoint) -> Node:

        # Virtual ConvergencePoint
        if isinstance(object, ConvergencePoint):
            return NodeSet(
                relations=[
                    create_node(structure[id][1])
                    for id in words.get(object.id, [])
                ]
            )

        # Logical NOT
        # TODO: if Type.NOT in object.types:

        # Logical entities
        relations = [
            create_node(structure[id][1])
            for id in words.get(object.id, [])
        ]
        return NodeEntity(
            entity=object.entity,
            relations=relations or None
        )

    if not roots:
        return Node(Type.EMPTY)
    nodes = [create_node(root) for root in roots]
    if len(nodes) == 1:
        return nodes[0]
    return Node(Type.SET, nodes)


def _create_relations(
        doc: stanza.Document,
        entities: list[Entity],
        patterns: dict[Type, list[re.Pattern]]
) -> Node:

    if not entities:
        return Node(Type.EMPTY)

    # TODO: Multi-Word / Multi-Token Entities
    # TODO: Entities refer to the entire text with start and end, e.g. beyond sentences

    relations = []
    for sentence in doc.sentences:
        # 1. Assignment of entities
        #    The remaining annotations for the entity relation are filled in
        #    during the second pass, as it may then be necessary to recognize
        #    other dependencies between entities. Since these do not occur
        #    continuously in the sentence, all entities must first be set.
        for word in sentence.words:
            # ignore MWT (Multi-Word Token without start_char)
            if word.start_char is None:
                continue
            for entity in entities:
                if entity.start <= word.start_char < entity.end:
                    word.entity = entity
                    break

        # 2. Annotate word with entities
        for word in sentence.words:
            if word.entity:
                _annotate_word(sentence, word, entity)

        # 3. Annotate relation-based path
        #    In the third pass, the relation-based path must be determined.
        #    However, this requires that the relation annotations for all
        #    entities are set correctly.
        for word in sentence.words:
            if word.entity:
                word.path = _get_word_relation_path(sentence, word)

        # X. Creating a flat tree structure of only the relevant entities
        structure = {word.id: (word.path, word) for word in sentence.words if word.types}

        # IMPORTANT: Do not shorten or simplify paths; IDs of irrelevant words
        # without entities can be potential convergence points that will be
        # needed later for the tree structure.

        relations.append(_create_relation_tree(structure))

    if not relations:
        return NodeEmpty()
    if len(relations) == 1:
        return relations[0]
    return NodeSet(relations=relations)


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


def _validate_language(language: str) -> str:
    language = (language or "").strip()
    if not language:
        raise ValueError("Language is required")
    if language.lower() not in set(_LANGUAGE_LOGIC_PATTERN.keys()):
        raise ValueError(f"Language '{language}' is not supported")
    return language.lower()


def _create_doc(language: str, text: str) -> stanza.Document:

    language = _validate_language(language)

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

    return doc


def pretty_print_sentence(sentence: Sentence):
    if not sentence:
        return
    if not isinstance(sentence, Sentence):
        raise TypeError(f"Unsupported type: {type(sentence)}")
    _print_sentence_tree(sentence)


def pretty_print_sentences(sentences: list[Sentence]):
    if not sentences:
        return
    if not isinstance(sentences, list):
        raise TypeError(f"Unsupported type: {type(sentences)}")
    if not all(isinstance(sentence, Sentence) for sentence in sentences):
        raise TypeError(f"Unsupported element type: {type(sentences)}")
    for sentence in sentences:
        _print_sentence_tree(sentence)


def pretty_print_node(node: Node):

    def is_node(object) -> bool:
        if isinstance(object, tuple) and len(object) == 2:
            type, value = object
            if isinstance(value, Entity):
                return True
            elif isinstance(value, list) and all(is_node(entry) for entry in value):
                return True
            elif value is None:
                return True
        return False

    if not node:
        return
    if not is_node(node):
        raise TypeError(f"Unsupported type: {type(node)}")
    _print_relation_tree(node)


def sentences(language: str, text: str) -> list[Sentence]:
    language = _validate_language(language)
    if not text.strip():
        return []
    return _create_doc(language, text).sentences


# TODO: entities must correspond to the output format and not the input format
#       correct is: (text, start, char, label)
#       https://spacy.io/usage/spacy-101#annotations-ner
#       or no, we keep simple tuples, as with spaCy input
def relations(language: str, text: str, entities: list[tuple[int, int, str]]) -> Node:
    language = _validate_language(language)
    if not text.strip() or not entities:
        return (Type.EMPTY, None)
    entities = [
        Entity(start, end, label, text[start:end])
        for start, end, label in entities
    ]
    return _create_relations(
        _create_doc(language, text),
        entities,
        _LANGUAGE_LOGIC_PATTERN[language]
    )
