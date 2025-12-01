# seanox_ai_npl/relations/relations.py

from __future__ import annotations

from collections import namedtuple

from seanox_ai_nlp.relations.abstract import Entity
from seanox_ai_nlp.relations.lang import languages, language_schema

from abc import ABC
from dataclasses import dataclass
from stanza.models.common.doc import Word, Sentence
from typing import NamedTuple

import os
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
    "cluster",
    default=None,
    getter=lambda self: getattr(self, "_cluster", ()),
    setter=lambda self, value: setattr(self, "_cluster", tuple(value))
)

Word.add_property(
    "entity",
    default=None,
    getter=lambda self: getattr(self, "_entity", None),
    setter=lambda self, value: setattr(self, "_entity", value)
)


class Substance(NamedTuple):
    path: tuple[int, ...]
    id: int
    cluster: int
    entity: Entity


# DESIGN DECISION:
# In the nodes, relations deliberately uses a union to document which object
# types are explicitly expected.

class Node(ABC):
    @property
    def name(self) -> str:
        name = self.__class__.__name__
        if name == "Node":
            return "NODE"
        return name.replace("Node", "").upper()


@dataclass(frozen=True)
class NodeEmpty(Node):
    def __eq__(self, other: object) -> bool:
        return isinstance(other, NodeEmpty)

    def __hash__(self) -> int:
        return hash(self.__class__)


@dataclass(frozen=True)
class NodeSet(Node):
    relations: tuple[NodeNot | NodeSet | NodeEntity, ...]

    def __eq__(self, other: object) -> bool:
        return isinstance(other, NodeSet) and frozenset(self.relations) == frozenset(other.relations)

    def __hash__(self) -> int:
        return hash((self.__class__, frozenset(self.relations)))


@dataclass(frozen=True)
class NodeNot(Node):
    relations: tuple[NodeNot | NodeSet | NodeEntity, ...]

    def __eq__(self, other: object) -> bool:
        return isinstance(other, NodeNot) and frozenset(self.relations) == frozenset(other.relations)

    def __hash__(self) -> int:
        return hash((self.__class__, frozenset(self.relations)))


@dataclass(frozen=True)
class NodeEntity(Node):
    entity: Entity

    def __eq__(self, other: object) -> bool:
        return isinstance(other, NodeEntity) and self.entity == other.entity

    def __hash__(self) -> int:
        return hash((self.__class__, self.entity))


_PIPELINES_MODEL_DIR = os.path.join(os.getcwd(), ".stanza")
_PIPELINES_CACHE: dict[tuple[str, str], stanza.Pipeline] = {}

TREE_SYMBOLS_BRANCH_ASCII = "+- "
TREE_SYMBOLS_END_ASCII    = "+- "
TREE_SYMBOLS_PIPE_ASCII   = "|  "
TREE_SYMBOLS_SPACE_ASCII  = "   "

TREE_SYMBOLS_BRANCH_UNICODE = "├─ "
TREE_SYMBOLS_END_UNICODE    = "└─ "
TREE_SYMBOLS_PIPE_UNICODE   = "│  "
TREE_SYMBOLS_SPACE_UNICODE  = "   "

TreeSymbols = namedtuple("TreeSymbols", ["BRANCH", "END", "PIPE", "SPACE"])
TREE_SYMBOLS = {
    True: TreeSymbols(
        TREE_SYMBOLS_BRANCH_UNICODE,
        TREE_SYMBOLS_END_UNICODE,
        TREE_SYMBOLS_PIPE_UNICODE,
        TREE_SYMBOLS_SPACE_UNICODE
    ),
    False: TreeSymbols(
        TREE_SYMBOLS_BRANCH_ASCII,
        TREE_SYMBOLS_END_ASCII,
        TREE_SYMBOLS_PIPE_ASCII,
        TREE_SYMBOLS_SPACE_ASCII
    )
}


def _print_sentence_tree(sentence: Sentence, unicode: bool = True) -> None:

    if not sentence:
        return

    nodes = {0: []}
    for word in sentence.words:
        nodes.setdefault(word.id, [])
        nodes.setdefault(word.head, []).append(word.id)

    symbols = TREE_SYMBOLS[unicode]

    def recurse(node_id: int, prefix: str = "", is_last: bool = True, is_root: bool = False):
        word = sentence.words[node_id - 1]
        label = f"{word.text} (id:{word.id}, head:{word.head}, lemma:{word.lemma}, upos:{word.upos}, deprel:{word.deprel}, feats:{word.feats})"
        connector = "" if is_root else (symbols.END if is_last else symbols.BRANCH)
        print(prefix + connector + label)

        # Only expand if a connector has been set
        prefix = prefix if is_root else prefix + (symbols.SPACE if is_last else symbols.PIPE)
        for index, relation_id in enumerate(nodes.get(node_id, [])):
            recurse(relation_id, prefix, index == len(nodes[node_id]) - 1)

    # Start directly with the node of ROOT (id 0),
    # without connector and without indentation
    root_nodes = nodes.get(0, [])
    for index, root_node_id in enumerate(root_nodes):
        recurse(root_node_id, "", index == len(root_nodes) - 1, is_root=True)


def _print_relation_tree(node: Node, unicode: bool = True) -> None:

    def recurse(node: Node, prefix: str = "", root: bool = True):

        if not isinstance(node, Node):
            return
        if not root and isinstance(node, NodeEmpty):
            return

        details = lambda node: f"label:{node.entity.label}, text:{node.entity.text}"

        # The type is only output here for the root node.
        # For recursive calls (root=False), the type was already output in the
        # previous print.
        if root:
            output = node.name
            if isinstance(node, NodeEntity):
                output = f"{output} ({details(node)})"
            print(output)

        if isinstance(node, NodeEmpty):
            return
        if not node.relations:
            return

        symbols = TREE_SYMBOLS[unicode]

        for index, relation in enumerate(node.relations):
            last = index == len(node.relations) - 1
            branch = symbols.END if last else symbols.BRANCH
            output = prefix + branch + relation.name
            if isinstance(relation, NodeEntity):
                print(f"{output} ({details(relation)})")
                continue
            print(output)
            recurse(relation, prefix + (symbols.SPACE if last else symbols.PIPE), root=False)

    recurse(node)


# For the creation of entity-relations from semantic text and the recognized
# entities, the processing is divided into three clearly separated layers: from
# the semantic text and entities, a logical representation of the entities is
# constructed via intermediate layers.
#
# 1. Linguistic Level (Stanza object)
# Sentence, Word, Entity from the NLP pipeline
# Raw data from linguistic analysis: token, lemma, upos, deprel, feats,
# start/end offset. This level is detailed, but too complex for direct logical
# processing.
#
# 2. Substances + Structure (intermediary)
# Substance (NamedTuple) + Structure (Mapping id -> (path, substance))
# Reduced meta-information (path, cluster, entity) of relevant words. This layer
# abstracts and extracts linguistic and logical details. It is one of the
# intermediate layers between the NLP output and the logical relationship.
#
# 3. Clustering / Normalization
# Substance + Node + Cluster (Mapping cluster id -> (path, cluster, node)
# Substances are grouped into clusters and form the basis for the tree topology
# through nesting. It is next one of the intermediate layers between the NLP
# output and the logical relationship.
#
# 4. Relations / Node-Tree
# Node, NodeSet, NodeEmpty, NodeEntity
# Logical representation of entities and their relationships. Here, the
# substances in the clusters are assembled into a tree or graph that maps the
# semantic relations (e.g. NOT, SET). This level is the basis for further
# processing, e.g. reasoning or queries.

def _create_relation_tree(structure: dict[int, tuple[tuple[int, ...], Substance]]) -> Node:

    # DESIGN DECISION:
    # Cluster is an internal class and can therefore be mutable. In contrast to
    # classes in general and module-related scope, where everything should be
    # immutable so that all consumers can rely on the content.

    @dataclass
    class Cluster:
        path: list[int]
        id: int
        head: int
        elements: list[Substance | Cluster]

    # Convert and group structure into cluster(s)
    clusters: dict[int, tuple[tuple[int, ...], Cluster, Node | None]] = {}

    # Initial creation of all clusters
    for id, (path, substance) in structure.items():
        for index in range(0, len(path)):
            if substance.path[index] in clusters:
                continue
            cluster = Cluster(
                id=substance.path[index],
                path=substance.path[:index + 1],
                head = substance.path[index - 1] if index > 0 else 0,
                elements=[]
            )
            clusters[cluster.id] = (cluster.path, cluster, None)

    # Assignment of substances to clusters
    for id, (path, substance) in structure.items():
        path, cluster, node = clusters[substance.cluster]
        cluster.elements.append(substance)

    # The node objects are determined and added to the clusters.
    # From this point on, the node objects form the final layer/view.
    for id, (path, cluster, node) in clusters.items():
        if cluster.id < 0:
            node = NodeNot(relations=[
                NodeEntity(entity=substance.entity)
                for substance in cluster.elements
            ])
        elif not cluster.elements:
            node = NodeSet(relations=[])
        elif len(cluster.elements) > 1:
            node = NodeSet(relations=[
                NodeEntity(entity=substance.entity)
                for substance in cluster.elements
            ])
        else:
            substance = cluster.elements[0]
            node = NodeEntity(entity=substance.entity)
        clusters[id] = (path, cluster, node)

    # Nesting is based on the insertion of clusters and nodes in their parents
    clusters = {id: (cluster, node) for id, (path, cluster, node) in clusters.items()}
    for id, (cluster, node) in clusters.items():
        if id != 0:
            parent = clusters.get(cluster.head)
            if parent:
                parent_cluster, parent_node = clusters[cluster.head]
                parent_cluster.elements.append(cluster)
                parent_node.relations.append(node)

    # Recursive determination of the root node
    # The root node is the first node that is not a NodeSet. Or a NodeSet that
    # has more than one relation.
    def find_root(node: Node) -> Node | None:
        if not isinstance(node, NodeSet):
            return node
        if len(node.relations) > 1:
            return node
        for relation in node.relations or []:
            relation = find_root(relation)
            if relation is not None:
                return relation
        return None
    cluster, node = clusters[0]
    node = find_root(node) or NodeEmpty()

    # The price for immutable nodes: Internally, you have to abandon the concept
    # and use mutable lists. Therefore, nodes must ultimately be finalized
    # recursively and changed to immutable nodes.

    def finalize(node: Node) -> Node:
        if isinstance(node, NodeEmpty):
            return node
        if isinstance(node, NodeEntity):
            return node
        if isinstance(node, NodeSet):
            # NodeSet may contain multiple NodeEntity instances referencing the
            # same Entity, e.g. due to multi-token spans. These duplicates are
            # removed within the same SET level.
            return NodeSet(
                relations=tuple({
                    finalize(relation)
                    for relation in node.relations
                })
            )
        if isinstance(node, NodeNot):
            return NodeNot(
                relations=tuple({
                    finalize(relation)
                    for relation in (node.relations or [])
                })
            )
        else:
            raise TypeError(f"Unsupported node type: {type(node)}")

    return finalize(node)


def _create_relations(doc: stanza.Document, entities: list[Entity]) -> Node:

    if not entities:
        return NodeEmpty()

    # DESIGN DECISION:
    #
    # The goal of this approach is to identify and group entities within a
    # sentence so that they can be used as logical units for a coarse prefilter
    # in retrieval. For the retrieval process, entities are categorized
    # meta-information, comparable to keywords -- in other words, a robust set
    # of candidate terms that do not attempt to capture full sentence semantics.
    #
    # The resulting structure is a tree, reduced to the smallest form while
    # preserving all logical relations (clusters and exclusions):
    # - Level 0: sentence root
    # - Level 1: main clusters (word-based entities)
    # - Level 2: synthetic exclusion nodes (structural, not tied to word IDs)
    # - Level 3: sub-clusters under exclusion
    #
    # Assuming that words gain their meaning within a sentence through the
    # context they form together. The meaning of a sentence emerges
    # compositionally from the meanings of its constituent parts. Each part of
    # the sentence contributes partial information, which together yields the
    # overall meaning.
    #
    # Concluding sentences are complex and highly variable word connections.
    # Capturing semantic meaning purely through rule-based approaches is not
    # feasible.
    #
    # The approach is based on consistently minimizing complexity. Words derive
    # their meaning in a sentence from the context they form together; the
    # overall meaning arises compositionally from the partial information of the
    # individual sentence components.
    #
    # To implement this, parts of the sentence are grouped into clusters, each
    # of which summarises words that are logically connected and must be
    # considered together. Instead of working directly with words, substance
    # objects with meta-information serve as abstract representations. All
    # clusters in a sentence together form a set that describes the overall
    # structure. Exclusions generate additional synthetic sub-clusters that can
    # include entities and sets.
    #
    # The structure begins at the sentence root (level 0). At level 1, main
    # clusters and independent exclusions are represented. Exclusions within
    # clusters appear as sub-clusters at deeper levels. Level 2 represents a
    # synthetic exclusion layer -- a technical construct introduced to
    # explicitly capture the presence of a negation or contrast. This layer acts
    # as a container that signals -- this sub-cluster in level 3 is excluded.
    # Multiple exclusions may be semantically nested, but are treated as a
    # single logical unit. They are flattened at level 2 and represented as part
    # of a cluster, while still preserving their role as candidate terms for
    # retrieval.
    #
    # Robustness
    #
    # It is important to understand that incorrect decisions or faulty logical
    # relationships can severely damage the quality of downstream pipelines,
    # even in a coarse prefilter. Therefore, the active fail-safe principle
    # applies:
    #
    # - Patterns are not only searched for that allow logical assignments,
    #   but also for patterns that challenge or contradict them.
    # - In cases of ambiguity, uncertainty, or contradictions, all relevant
    #   entities are collected into a single cluster instead of making risky
    #   assumptions.
    #
    # This approach prevents faulty pre-decisions from destroying the semantic
    # integrity of the overall structure.

    schema = language_schema(doc.lang)

    relations = []
    for sentence in doc.sentences:

        # Annotate words, path, cluster, and entity are set.
        # Ignore MWT (Multi-Word Token without start_char).
        schema.annotate_words(sentence, entities)
        schema.refinement_words(sentence, entities)

        words: list[Word] = [word for word in sentence.words if word.entity is not None]
        if not words:
            continue

        # Create a flat tree structure of Substance object for all relevant
        # words. Substance is reduced meta-information about a word that is
        # required for building logical relationships. Enclosed by structure, it
        # forms an explicit intermediate layer between the linguistic data
        # (stanza) and the final entity relationships (node tree).
        structure: dict[int, tuple[tuple[int, ...], Substance]] = {
            word.id: (
                word.cluster,
                Substance(
                    path=word.cluster,
                    id=word.id,
                    cluster=word.cluster[-1],
                    entity=word.entity
                )
            )
            for word in words
        }

        # IMPORTANT: Do not shorten or simplify paths; IDs of irrelevant words
        # without entities can be potential convergence points, exclusions that
        # will be needed later for the tree structure.

        relations.append(_create_relation_tree(structure))

    relations = tuple(dict.fromkeys(relations))
    if not relations:
        return NodeEmpty()
    if len(relations) == 1:
        return relations[0]
    return NodeSet(relations=relations)


def _download_pipeline_lazy(lang: str) -> None:
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

    preprocessor = language_schema(lang).sentence_preprocessor()
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


def pretty_print_sentence(sentence: Sentence, unicode: bool = True) -> None:
    """
    Print a human-readable tree representation of a single parsed sentence.

    This function visualizes the syntactic dependency structure of a sentence
    using a tree layout. It is primarily intended for debugging and inspection
    of the linguistic analysis performed by Stanza.

    Args:
        sentence (Sentence): A Stanza Sentence object to be printed.

    Raises:
        TypeError: If the input is not a Sentence instance.
    """
    if not sentence:
        return
    if not isinstance(sentence, Sentence):
        raise TypeError(f"Unsupported type: {type(sentence)}")
    _print_sentence_tree(sentence, unicode)


def pretty_print_sentences(sentences: list[Sentence], unicode: bool = True) -> None:
    """
    Print human-readable tree representations for a list of parsed sentences.

    Each sentence is visualized individually in a tree layout that shows
    syntactic dependencies. This is useful for inspecting multiple sentences
    from a document or text input.

    Args:
        sentences (list[Sentence]): A list of Stanza Sentence objects.

    Raises:
        TypeError: If the input is not a list of Sentence instances or contains
            unsupported element types.
    """
    if not sentences:
        return
    if not isinstance(sentences, list):
        raise TypeError(f"Unsupported type: {type(sentences)}")
    if not all(isinstance(sentence, Sentence) for sentence in sentences):
        raise TypeError(f"Unsupported element type: {type(sentences)}")
    for sentence in sentences:
        _print_sentence_tree(sentence, unicode)


def pretty_print_node(node: Node, unicode: bool = True) -> None:
    """
    Print a human-readable tree representation of a relation node.

    This function visualizes the logical structure of entities and their
    relationships in a tree layout. It is primarily intended for debugging
    and inspection of the relation graph created from text and entities.

    Args:
        node (Node): The root node of the relation tree to be printed.

    Raises:
        TypeError: If the input is not a Node instance.
    """
    if not isinstance(node, Node):
        raise TypeError(f"Unsupported type: {type(node)}")
    _print_relation_tree(node, unicode)


def sentences(lang: str, text: str) -> list[Sentence]:
    """
    Parse text into sentences using a Stanza NLP pipeline.

    This function validates the language code, creates a Stanza document for
    the given text, and returns the parsed sentences. Each sentence contains
    tokens, lemmas, part-of-speech tags, and dependency relations.

    Args:
        lang (str): Language code (e.g. "de", "en").
        text (str): Input text to be analyzed.

    Returns:
        list[Sentence]: A list of Stanza Sentence objects representing the
        parsed sentences. Returns an empty list if the text is blank.

    Raises:
        ValueError: If the language code is missing or unsupported.
    """
    lang = _validate_language(lang)
    if not text.strip():
        return []
    return _create_doc(lang, text).sentences


# DESIGN DECISION:
# Simple tuples based on the spaCy input format for ents are used; the detail
# fields of the output format are deliberately omitted in order to keep the
# structure lean and consistent.

def relations(lang: str, text: str, entities: list[tuple[int, int, str]], semantic: bool = True) -> Node:
    """
    Build a logical relation tree from text and annotated entities.

    This function parses the input text using a Stanza NLP pipeline, enriches
    the recognized entities with linguistic features, and constructs a logical
    relation tree. The resulting Node structure represents semantic relations
    such as SET and NOT between entities, providing a normalized view of the
    text's logical meaning.

    Args:
        lang (str): Language code (e.g. "de", "en").
        text (str): Input text to be analyzed.
        entities (list[tuple[int, int, str]]): List of entity spans as
            (start_index, end_index, label). The text substring between
            start_index and end_index is automatically extracted.
        semantic (bool, optional): Controls how entities that occur multiple
            times on a level are handled.
            - If True (default), the equality of nodes is determined only by
              label and text of the contained entity. Multiple occurrences of
              entities at the same level are prevented. This produces a
              normalized, meaning-oriented relation tree.
            - If False, all occurrences of the entities are retained at the same
              level. This produces a form-oriented relation tree that reflects
              the original wording.

    Returns:
        Node: Root node of the relation tree representing logical structure
        between entities. Returns NodeEmpty if no entities are provided or
        the text is blank.

    Raises:
        ValueError: If the language code is missing or unsupported.
        TypeError: If the input types are invalid.
    """
    lang = _validate_language(lang)
    if not text.strip() or not entities:
        return NodeEmpty()
    entities = [
        Entity(start, end, label, text[start:end], semantic)
        for start, end, label in entities
    ]
    return _create_relations(
        _create_doc(lang, text),
        entities
    )
