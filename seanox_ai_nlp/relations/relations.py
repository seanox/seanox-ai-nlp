# seanox_ai_npl/relations/relations.py

from seanox_ai_nlp.relations.lang import languages, language_module

from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum, auto
from stanza.models.common.doc import Word, Sentence
from typing import Optional, Union, NamedTuple, FrozenSet

import os
import re
import stanza


# DESIGN DECISION:
# Use "lang" for a single language code (e.g. de, en) to follow common API
# conventions. Use "languages" for the set of all supported codes. The full word
# in plural form is more pythonic and idiomatic, improving readability and
# auditability compared to "langs".


# Custom annotation slots (properties) for entity relations.
# stanza.Word is a central object and is extended with additional meta
# information through these properties.

Word.add_property(
    "path",
    default=None,
    getter=lambda self: getattr(self, "_path", ()),
    setter=lambda self, value: setattr(self, "_path", tuple(value))
)

Word.add_property(
    "entity",
    default=None,
    getter=lambda self: getattr(self, "_entity", None),
    setter=lambda self, value: setattr(self, "_entity", value)
)


class Type(Enum):
    EMPTY = auto()
    SET = auto()
    NOT = auto()
    INVERT = auto()
    ENTITY = auto()


class Entity(NamedTuple):
    start: int
    end: int
    label: str
    text: str


class Substance(NamedTuple):
    path: tuple[int, ...]
    id: int
    relation: int
    word: Word
    entity: Entity
    types: FrozenSet[str] = frozenset()


@dataclass
class NodeEmpty:
    type: Type = field(init=False, default=Type.EMPTY)


@dataclass
class NodeSet:
    type: Type = field(init=False, default=Type.SET)
    relations: list[Union["NodeNot", "NodeSet", "NodeEntity"]]

    def __post_init__(self):
        if not self.relations:
            raise ValueError("Relations are required")


@dataclass
class NodeEntity:
    type: Type = field(init=False, default=Type.ENTITY)
    entity: Entity
    relations: Optional[list[Union["NodeNot", "NodeSet", "NodeEntity"]]] = None


@dataclass
class NodeNot:
    type: Type = field(init=False, default=Type.NOT)
    relations: list[Union["NodeNot", "NodeSet", "NodeEntity"]] = None

    def __post_init__(self):
        if not self.relations:
            raise ValueError("Relations are required")


Node = Union[NodeEmpty, NodeNot, NodeSet, NodeEntity]


_PIPELINES_MODEL_DIR = os.path.join(os.getcwd(), ".stanza")
_PIPELINES_CACHE: dict[tuple[str, str], stanza.Pipeline] = {}


def _re_compile_logic_pattern(*pattern: str) -> re.Pattern:
    return re.compile(
        rf"(?i)^({'|'.join([f'(?:{pattern})' for pattern in pattern])})$"
    )


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


def _get_word_path(sentence: Sentence, word: Word) -> tuple[int, ...]:
    path: list[int] = []
    while True:
        path.insert(0, word.head)
        if word.head <= 0:
            break
        word = sentence.words[word.head - 1]
    return tuple(path)


def _get_substance_path(substances: dict[int, Substance], substance: Substance) -> tuple[int, ...]:
    path: list[int] = []
    while True:
        path.insert(0, substance.relation)
        if substance.relation <= 0:
            break
        substance = substances[substance.relation]
    return tuple(path)


def _create_substance(lang: str, sentence: Sentence, word: Word, entity: Entity) -> Substance:

    # Abstracts:
    # - unusual/ambiguous sentence structure, then do not use NOT

    # Every entity is ENTITY
    types = {Type.ENTITY}

    # TODO:
    # NOT is more complex
    # - in ambiguous/contradictory cases, NOT must be omitted
    # - NOT can/must also be recognized through keywords and spread phrases
    for relation in sentence.words:
        if relation.head != word.id:
            continue
        if relation.deprel == "neg":
            types.add(Type.NOT)
        if relation.feats:
            feats = _get_word_feats(relation)
            if "Polarity" in feats and feats["Polarity"] == "Neg":
                types.add(Type.NOT)
            elif "PronType" in feats and feats["PronType"] == "Neg":
                types.add(Type.NOT)
            elif "Negative" in feats and feats["Negative"] == "Neg":
                types.add(Type.NOT)
    if word.deprel == "neg":
        types.add(Type.NOT)

    module = language_module(lang)

    # Relation is initially based on UD and the head from the stanza word, but
    # in order to correctly map UNION, SET, and NOT, this must be adjusted using
    # extended language-specific rules.
    return Substance(
        path=None,
        id=word.id,
        relation=module.infer_logical_relation(sentence, word),
        types=types,
        word=word,
        entity=entity
    )


def _print_relation_tree(node: Node):

    def recurse(node: Node, prefix: str = "", root: bool = True):

        if not isinstance(node, Node):
            return
        if not root and isinstance(node, NodeEmpty):
            return

        # The type is only output here for the root node.
        # For recursive calls (root=False), the type was already output in the
        # previous print().
        if root:
            output = node.type.name
            if isinstance(node, NodeEntity):
                output = f"{output} (label:{node.entity.label}, text:{node.entity.text})"
            print(output)

        if isinstance(node, NodeEmpty):
            return
        if not node.relations:
            return

        for index, relation in enumerate(node.relations):
            last = index == len(node.relations) - 1
            branch = "└─ " if last else "├─ "
            output = prefix + branch + relation.type.name
            if isinstance(relation, NodeEntity):
                output = f"{output} (label:{relation.entity.label}, text:{relation.entity.text})"
            print(output)
            recurse(relation, prefix + ("   " if last else "│  "), root=False)

    recurse(node)


# For the creation of entity-relations from semantic text and the recognized
# entities, the processing is divided into three clearly separated layers: from
# the semantic text and entities, a logical representation of the entities is
# constructed via an auditable intermediate layer.
#
# 1. Linguistic Level (Stanza object)
# Sentence, Word, Entity from the NLP pipeline
# Raw data from linguistic analysis: tokens, lemmas, dependencies, start/end
# offsets. This level is detailed, but too complex, too raw and too strict  for
# direct logical processing.
#
# 2. Substances + Structure (intermediary)
# Substance (NamedTuple) + Structure (Mapping id -> (path, substance))
# Reduced, immutable snapshots of relevant words, enriched with additional
# fields (path, types, entity). This layer abstracts linguistic details and
# makes them auditable, reproducible, and stable. It is the explicit
# intermediate layer between NLP output and logical relation.
#
# 3. Relations / Node‑Tree
# Node, NodeSet, NodeEmpty, ConvergencePoint
# Logical representation of entities and their relationships. Here, the
# substances are assembled into a tree or graph that maps the semantic relations
# (e.g. UNION, NOT, SET). This level is the basis for further processing, e.g.
# reasoning or queries.

def _create_relation_tree(structure: dict[int, tuple[list[int], Substance]]) -> Node:

    class ConvergencePoint(NamedTuple):
        path: list[int]
        id: int
        relation: int
        types: set[str]
        entity: Optional[Entity] = None

    structure = structure.copy()

    # Find convergence points (joins) in the paths that do not exist as separate
    # substances in the structure. A synthetic element with type SET will later
    # be created for each of these convergence points so that the logical
    # nesting and branching below the entities is displayed correctly.
    # Convergence points are determined from right to left. As soon as an
    # existing reference point is found in structure, the search is terminated
    # because the remaining path is already covered by this reference point in
    # structure.
    relations: dict[int, list[list[int]]] = defaultdict(list)
    for id, (path, substance) in structure.items():
        for index in reversed(range(len(path))):
            relation = path[index]
            if relation in structure:
                break
            if relation > 0:
                relations[relation].append(path[:index] or [relation])

    for relation, paths in relations.items():
        if len(paths) > 1:
            structure[relation] = (
                paths[0],
                ConvergencePoint(
                    path=paths[0],
                    id=relation,
                    relation=paths[0][-1],
                    types={Type.SET}
                )
            )

    # Normalize paths
    # - only keep parent/relation IDs that are valid keys in structure
    # - and keep 0 as an indicator for ROOT so that paths are never empty
    relations = set(structure.keys())
    for id, (path, substance) in list(structure.items()):
        structure[id] = (
            [relation for relation in path if relation == 0 or relation in relations],
            substance
        )

    # Root is determined either directly via path [0] or the shortest path
    roots = [substance for id, (path, substance) in structure.items() if path == [0]]
    if not roots:
        width = min(len(path) for path, substance in structure.values())
        roots = [substance for path, substance in structure.values() if len(path) == width]

    # Reference table substances:[relations IDs]
    # It serves as a reference work for directly accessing the IDs of
    # subordinate substances from a word ID.
    substances: dict[int, list[int]] = {id: [] for id in structure}
    for id, (path, substance) in structure.items():
        if substance not in roots:
            relation = path[-1]
            if relation in substances and relation != id:
                substances[relation].append(id)

    def create_node(object: Substance | ConvergencePoint) -> Node:
        # Virtual ConvergencePoint
        if isinstance(object, ConvergencePoint):
            return NodeSet(
                relations=[
                    create_node(structure[id][1])
                    for id in substances.get(object.id, [])
                ]
            )

        # Logical NOT
        # TODO: if Type.NOT in object.types:

        # Logical entities
        relations = [
            create_node(structure[id][1])
            for id in substances.get(object.id, [])
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


def _create_relations(doc: stanza.Document, entities: list[Entity]) -> Node:

    if not entities:
        return Node(Type.EMPTY)

    # TODO: Multi-Word / Multi-Token Entities
    # TODO: Entities refer to the entire text with start and end, e.g. beyond sentences

    relations = []
    for sentence in doc.sentences:

        # 1. Annotate words and detect words relevant to entities
        #    Ignore MWT (Multi-Word Token without start_char).
        #    In addition, mark words that refer to entities by assigning the
        #    respective entity to the word. This allows the logical meaning of a
        #    word to be correctly evaluated later in the sentence and entity
        #    context.
        words: dict[Word, list[Entity]] = defaultdict(list)
        for word in sentence.words:
            word.path = _get_word_path(sentence, word)
            if word.start_char is not None:
                for entity in entities:
                    if entity.start <= word.start_char < entity.end:
                        words[word].append(entity)
                        word.entity = entity
                        break

        # 2. Create a Substance object for all relevant words.
        #    Substance is a reduced snapshot of Word, enriched with additional
        #    fields (e.g. types, word, entity and relation for head) that are
        #    required for building logical relationships. Enclosed by structure,
        #    it forms an explicit intermediate layer between the linguistic data
        #    (stanza) and the final entity relationships (node tree).
        #
        #    Because Substance is immutable/read-only, its construction requires
        #    two passes: in the first pass, raw Substances are created with
        #    basic fields (id, relation, entity, etc.); in the second pass, once
        #    all relation are known, the correct dependency path can be computed
        #    and new enriched Substances are produced. This ensures consistency
        #    and auditability without mutating existing objects.
        substances: dict[int, Substance] = {}
        for word in words:
            for entity in words[word]:
                substance = _create_substance(doc.lang, sentence, word, entity)
                substances[substance.id] = substance

        # 3. Finalizing the substance with the correct dependency path
        substances = [
            substance._replace(path=_get_substance_path(substances, substance))
            for substance in substances.values()
        ]

        # X. Creating a flat tree structure of entities based on substances
        structure = {substance.id: (substance.path, substance) for substance in substances}

        # IMPORTANT: Do not shorten or simplify paths; IDs of irrelevant words
        # without entities can be potential convergence points that will be
        # needed later for the tree structure.

        relations.append(_create_relation_tree(structure))

    if not relations:
        return NodeEmpty()
    if len(relations) == 1:
        return relations[0]
    return NodeSet(relations=relations)


def _download_pipeline_lazy(lang: str):
    if os.path.exists(os.path.join(_PIPELINES_MODEL_DIR, lang)):
        return
    stanza.download(lang, model_dir=_PIPELINES_MODEL_DIR)


def _get_pipeline(lang: str, processors: str | None) -> stanza.Pipeline:

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

    key = (lang, processors)
    if key not in _PIPELINES_CACHE:
        _download_pipeline_lazy(lang)
        _PIPELINES_CACHE[key] = stanza.Pipeline(
            lang=lang,
            processors=processors,
            tokenize_pretokenized=not tokenizer,
            model_dir=_PIPELINES_MODEL_DIR,
            download_method=None,
            use_gpu=False
        )
    return _PIPELINES_CACHE[key]


def _validate_language(lang: str) -> str:
    lang = (lang or "").strip()
    if not lang:
        raise ValueError("Language is required")
    if lang.lower() not in languages():
        raise ValueError(f"Unsupported language: {lang}")
    return lang.lower()


def _create_doc(lang: str, text: str) -> stanza.Document:

    lang = _validate_language(lang)

    # DESIGN DECISION:
    # stanza.models.common.doc
    # https://github.com/stanfordnlp/stanza/blob/main/stanza/models/common/doc.py
    # The property "lang" is set by Design to None, so it is set manually.
    # doc.lang is only used internally; the public API uses a separate "lang".

    preprocessor = language_module(lang).sentence_preprocessor()
    if preprocessor is not None:

        # First pass as a preprocess to change everyday logical words and
        # phrases in Universal Dependencies words and phrases so that the stanza
        # pipelines can interpret them.
        nlp = _get_pipeline(lang, processors="tokenize,mwt")
        doc = nlp(text)
        doc.lang = lang
        sentences = []
        for sentence in doc.sentences:
            sentences.append(preprocessor(sentence))

        # Second pass to determine the actual logical structure.
        nlp = _get_pipeline(lang, processors="pos,lemma,depparse")
        doc = nlp(sentences)
        doc.lang = lang
    else:
        nlp = _get_pipeline(lang, processors="tokenize,mwt,pos,lemma,depparse")
        doc = nlp(text)
        doc.lang = lang

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
    if not isinstance(node, Node):
        raise TypeError(f"Unsupported type: {type(node)}")
    _print_relation_tree(node)


def sentences(lang: str, text: str) -> list[Sentence]:
    lang = _validate_language(lang)
    if not text.strip():
        return []
    return _create_doc(lang, text).sentences


# DESIGN DECISION:
# Simple tuples based on the spaCy input format for ents are used; the detail
# fields of the output format are deliberately omitted in order to keep the
# structure lean and consistent.

def relations(lang: str, text: str, entities: list[tuple[int, int, str]]) -> Node:
    lang = _validate_language(lang)
    if not text.strip() or not entities:
        return (Type.EMPTY, None)
    entities = [
        Entity(start, end, label, text[start:end])
        for start, end, label in entities
    ]
    return _create_relations(
        _create_doc(lang, text),
        entities
    )
