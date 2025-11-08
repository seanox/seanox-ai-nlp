# seanox_ai_npl/relations/relations.py

from __future__ import annotations

from seanox_ai_nlp.relations.lang import languages, language_schema
from seanox_ai_nlp.relations.lang.abstract import Feature

from abc import ABC
from collections import defaultdict
from dataclasses import dataclass
from stanza.models.common.doc import Word, Sentence
from typing import Optional, NamedTuple, FrozenSet

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


class Entity(NamedTuple):
    start: int
    end: int
    label: str
    text: str


class Substance(NamedTuple):
    path: tuple[int, ...]
    id: int
    head: int
    cluster: int
    word: Word
    entity: Entity
    features: FrozenSet[Feature] = frozenset()


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
    ...


@dataclass(frozen=True)
class NodeSet(Node):
    relations: tuple[NodeNot | NodeSet | NodeEntity, ...]


@dataclass(frozen=True)
class NodeNot(Node):
    relations: tuple[NodeNot | NodeSet | NodeEntity, ...]


@dataclass(frozen=True)
class NodeEntity(Node):
    entity: Entity


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
    path: list[int] = [substance.cluster]
    while True:
        path.insert(0, substance.head)
        if substance.head <= 0:
            break
        substance = substances.get(substance.head)
    return tuple(path)


def _create_substance(lang: str, sentence: Sentence, word: Word, entity: Entity) -> Substance:

    schema = language_schema(lang)

    # There are two types of relations:
    #
    # 1. head (dependency): refers to the parent substance.
    #    - The value always starts at 0 (root)
    #    - Must be explicitly determined using semantic rules
    #
    # 2. cluster: refers to the grouping of related substances.
    #    - Determined using rules based on UD features
    #      deprel + upos from Universal Dependencies
    #
    # Together, head and cluster provide a bidirectional view of the relation
    # structure. To correctly represent logical constructs such as SET and NOT,
    # these relations must be further refined using extended, language-specific
    # rules.

    relation = schema.infer_relation(sentence, word)
    return Substance(
        path=None,
        id=word.id,
        head=relation.head,
        cluster=relation.cluster,
        features=relation.features,
        word=word,
        entity=entity
    )


def _print_relation_tree(node: Node):

    def recurse(node: Node, prefix: str = "", root: bool = True):

        if not isinstance(node, Node):
            return
        if not root and isinstance(node, NodeEmpty):
            return

        details = lambda node: f"label:{node.entity.label}, text:{node.entity.text}"

        # The type is only output here for the root node.
        # For recursive calls (root=False), the type was already output in the
        # previous print().
        if root:
            output = node.name
            if isinstance(node, NodeEntity):
                output = f"{output} ({details(node)})"
            print(output)

        if isinstance(node, NodeEmpty):
            return
        if not node.relations:
            return

        for index, relation in enumerate(node.relations):
            last = index == len(node.relations) - 1
            branch = "└─ " if last else "├─ "
            output = prefix + branch + relation.name
            if isinstance(relation, NodeEntity):
                print(f"{output} ({details(relation)})")
                continue
            print(output)
            recurse(relation, prefix + ("   " if last else "│  "), root=False)

    recurse(node)


# For the creation of entity-relations from semantic text and the recognized
# entities, the processing is divided into three clearly separated layers: from
# the semantic text and entities, a logical representation of the entities is
# constructed via intermediate layers.
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
# fields (path, features, entity). This layer abstracts and extracts linguistic
# details. It is one of the intermediate layers between the NLP output and the
# logical relationship.
#
# 3. Clustering / Normalization
# Substance + Node + Cluster (Mapping cluster id -> (path, cluster, node)
# Substances are grouped into clusters, synthetic clusters are inserted for
# convergence points and opposition (NEGATION and CONTRAST), and paths are
# normalized. The result: a consistent tree topology. It is next one of the
# intermediate layers between the NLP output and the logical relationship.
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
        path: tuple[int, ...]
        id: int
        head: int
        elements: list[Substance | Cluster]
        features: set[Feature]

    @dataclass
    class ClusterNot(Cluster):
        ...

    # Convert and group structure into cluster(s)
    clusters: dict[int, tuple[tuple[int, ...], Cluster, Optional[Node]]] = {}
    for id, (path, substance) in structure.items():
        if substance.cluster not in clusters:
            cluster = Cluster(path=None, id=substance.cluster, head=0, elements=[], features=())
            clusters[substance.cluster] = (None, cluster, None)
        path, cluster, node = clusters[substance.cluster]
        # The primary substance of a cluster determines its features and path.
        if substance.id == substance.cluster:
            path = tuple(substance.path)
            cluster = Cluster(
                path=path,
                id=substance.cluster,
                head=path[-2] if len(path) >= 2 else 0,
                elements=cluster.elements,
                features=None
            )
            # NEGATION and CONTRAST are first inserted as loose negative
            # clusters, and later the paths are adjusted to all clusters and
            # substances. With the negative ID, the clusters retain an implicit
            # and simple relationship, and overlaps are prevented.
            if Feature.NEGATION in substance.features or Feature.CONTRAST in substance.features:
                opposition = ClusterNot(
                    path=path[:-1] + (-substance.cluster, substance.cluster),
                    id=-substance.cluster,
                    head=cluster.head,
                    elements=[cluster],
                    features=substance.features
                )
                clusters[opposition.id] = (opposition.path, opposition, None)
        cluster.elements.append(substance)
        clusters[substance.cluster] = (path, cluster, None)

    # NEGATION and CONTRAST clusters (restricted to the cluster level), as well
    # as the relevant elements, are assigned or re-assigned by adjusting paths
    # and head. Only negative clusters need to be considered during iteration,
    # as the relevant elements can be determined via the corresponding positive
    # ID.

    # For each positive ID that has a negative counterpart, iterate through all
    # clusters. If a path contains the positive ID but not the negative one,
    # update the element:
    # - set its head to the negative ID
    # - insert the negative ID directly before the positive ID in its path
    # Finally, write the updated path and cluster back into the dictionary.

    positives = [abs(id) for id in clusters if id < 0]
    for positive in positives:
        for id, (path, cluster, node) in clusters.items():
            if positive not in path or -positive in path:
                continue
            cluster.head = -positive
            index = path.index(positive)
            cluster.path = path[:index] + (-positive,) + path[index:]
            clusters[id] = (cluster.path, cluster, None)

    # Find convergence points (branches) in the paths that do not exist as
    # separate cluster in the clusters. A synthetic cluster without element
    # will later be created for each of these convergence points so that the
    # logical nesting and branching below the entities is displayed correctly.
    # Convergence points are determined from right to left. As soon as an
    # existing reference point is found in structure, the search is terminated
    # because the remaining path is already covered by this reference point in
    # structure.

    # relations collects subpaths of cluster paths that are not already covered
    # by other cluster nodes. This captures the “gaps” in the hierarchy path
    # that may later become convergence points.
    relations: dict[int, list[list[int]]] = defaultdict(list)
    for id, (path, cluster, node) in clusters.items():
        for index in reversed(range(len(path))):
            relation = path[index]
            if relation in clusters:
                break
            if relation > 0:
                relations[relation].append(path[:index] or [relation])

    # For convergence points without clusters, synthetic clusters without
    # elements are inserted. These clusters will be needed later for nesting.
    for relation, paths in relations.items():
        if len(paths) > 1:
            path = paths[0]
            head = path[-2] if len(path) >= 2 else 0
            clusters[relation] = (
                path, Cluster(path=path, id=relation, head=head, elements=[], features=()), None
            )

    # Normalize paths (in the dict and in the cluster objects)
    # - only keep parent/relation IDs that are valid keys in clusters
    # - and keep 0 as an indicator for ROOT so that paths are never empty
    relations = set(clusters.keys())
    for id, (path, cluster, node) in list(clusters.items()):
        path = tuple(relation for relation in path if relation == 0 or relation in relations)
        cluster = Cluster(
            path=path,
            id=cluster.id,
            head=path[-2] if len(path) >= 2 else 0,
            elements=cluster.elements,
            features=cluster.features
        )
        clusters[id] = (path, cluster, None)

    # Insert a root cluster (id=0, head=0) only if necessary:
    # - no root cluster exists yet, and
    # - and there are at least two clusters with different root path prefixes
    # In that case, the root cluster serves as a container to enable proper
    # nesting.
    if 0 not in clusters:
        roots = {tuple(path[:2]) for path, cluster, node in clusters.values() if len(path) >= 2}
        if len(roots) > 1:
            clusters[0] = (
                (0,), Cluster(path=(0,), id=0, head=0, elements=[], features=()), None
            )

    # The node objects are determined and added to the clusters. From this point
    # on, the node objects form the final layer/view.
    for id, (path, cluster, node) in clusters.items():

        # Substances and clusters are permitted as elements, but at this stage
        # only substances and clusters in the form of convergence points may be
        # included. Other clusters would be an error.

        # without elements, it must be a convergence point
        if not cluster.elements:
            node = NodeSet(relations=[])
        elif len(cluster.elements) > 1:
            # NEGATION and CONTRAST substances (restricted to the substances level):
            # - Substances carrying NEGATION or CONTRAST are wrapped as NodeNot
            # - All other Substances are added directly as NodeEntity
            create_relations = lambda substance: (
                NodeNot(relations=[NodeEntity(entity=substance.entity)])
                if substance.features and (Feature.NEGATION in substance.features or Feature.CONTRAST in substance.features)
                else NodeEntity(entity=substance.entity)
            )
            node = NodeSet(relations=[create_relations(substance) for substance in cluster.elements])
        else:
            node = NodeEntity(entity=cluster.elements[0].entity)
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

    # root element is determined via the shortest path
    id, (cluster, node) = min(
        clusters.items(),
        key=lambda item: len(item[1][0].path)
    )

    # The price for immutable nodes: Internally, you have to abandon the concept
    # and use mutable lists. Therefore, nodes must ultimately be finalized
    # recursively and changed to immutable nodes.

    def finalize(node: Node) -> Node:
        if isinstance(node, NodeEmpty):
            return node
        if isinstance(node, NodeEntity):
            return node
        if isinstance(node, NodeSet):
            return NodeSet(
                relations=tuple(finalize(relations) for relations in node.relations)
            )
        if isinstance(node, NodeNot):
            return NodeNot(
                relations=tuple(finalize(relations) for relations in (node.relations or []))
            )
        else:
            raise TypeError(f"Unsupported node type: {type(node)}")

    return finalize(node)


def _create_relations(doc: stanza.Document, entities: list[Entity]) -> Node:

    if not entities:
        return NodeEmpty()

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
        #    fields (e.g. features, word, entity and relation for head) that are
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
        return NodeEmpty
    entities = [
        Entity(start, end, label, text[start:end])
        for start, end, label in entities
    ]
    return _create_relations(
        _create_doc(lang, text),
        entities
    )
