# Introduction

Natural texts often contain terms that stand in implicit logical relationships
to one another -- for example, inclusion or exclusion relationships. The use of
modern AI systems for processing large amounts of data has shown that many
methods trained on general language usage, but without large language models,
can be too imprecise when applied to technical domain languages such as those
in industry and government. This module addresses this issue: it is intended to
identify categorized terms and their relationships using methods of natural
language processing and to represent them in a transparent, verifiable logical
structure -- independently of large language models. The resulting bridge
between language and logic provides a foundation on which existing AI systems
can continue to build.

The module focuses on robust data structures and modular NLP pipelines. The
linguistic analysis is based on __[stanza](
    https://stanfordnlp.github.io/stanza/)__ with __[Universal Dependencies](
    https://universaldependencies.org/)__ and uses __[dependency relations
(deprel)](https://universaldependencies.org/u/dep/all.html)__ to capture
syntactic dependencies more precisely. These relations form the foundation for
systematically identifying implicit logical structures such as inclusion,
exclusion, or nesting.

In addition, __language-specific keywords with logical meaning are taken from
configurable lexicons__, ensuring that the approach remains modular and can be
easily extended to additional languages.

Building on this, the __Entity Relation Composer__ establishes a rule-based logic
layer that implements the principles of __[Entity Relation Semantics (ERS)](
    #entity-relation-semantics-ers)__ as described below. It processes entities
from upstream components and represents their relations using the basic
constructs __SET__ (grouping or relation) and __NOT__ (exclusion). Enumerations
are always interpreted as sets, making an explicit __OR__ unnecessary, while an
__AND__ in the sense of a strict intersection does not exist; instead,
expressive power arises through combination, nesting, and normalization.
Restrictions or entity bindings (__WITH__) do not require an explicit operator
either, since they are expressed implicitly through tree structure and nesting.
The resulting logical structure can be expressed in __SQL, JSON, or YAML__ and
serves downstream components as a foundation for search or filtering.

This approach is __neither complete nor perfect__ and will __never replace a
large language model (LLM)__ -- natural language is far too complex for
exhaustive rule-based coverage. Instead, it offers a __practical and extensible
foundation__ for building __interpretable retrieval logic__. It functions as a
__deterministic filter__: reducing noise, capturing inclusion and exclusion
markers, and providing a transparent pre-retrieval layer on which more complex
semantic or neural models can operate more efficiently.

# Features

# Table Of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Entity Relation Semantics (ERS)](#entity-relation-semantics-ers)
  - [Example](#example)
- [Known Limitations](#known-limitations)
- [Usage](#usage)
- [Benchmark](#benchmark)
- [API](#api)
  - [Reference](#reference)
    - [`sentences`](#sentenceslang-str-text-str---listsentence)
    - [`relations`](#relationslang-str-text-str-entities-listtupleint-int-str---node)
    - [`pretty_print_sentence`](#pretty_print_sentencesentence-sentence---none)
    - [`pretty_print_sentences`](#pretty_print_sentencessentences-listsentence---none)
    - [`pretty_print_node`](#pretty_print_nodenode-node---none)
    - [`Entity`](#entity)
    - [`Node`](#node)
    - [`NodeEmpty`](#nodeempty)
    - [`NodeEntity`](#nodeentity)
    - [`NodeSet`](#nodeset)
    - [`NodeNot`](#nodenot)
- [System Design](#system-design)
- [Concepts](#concepts)
- [Sources & References](#sources--references)

# Entity Relation Semantics (ERS)

__Interpret logic in a retrieval-oriented manner -- not as full semantic
reasoning, and not as formal-mathematical logic.__

__Entity Relation Semantics (ERS)__ functions as a __pre-retrieval stage__ in
the information retrieval pipeline. It applies only __lightweight,
coarse-grained logic__ based on linguistically stable inclusion and exclusion
markers -- such as negators or simple verb particles -- which are often
detectable in a rule-based manner and help reduce noise. ERS thus provides a
__transparent, deterministic filtering layer__ that narrows the candidate set
for downstream processes without attempting full semantic interpretation.

Everything mentioned is interpreted by default as a __set (SET)__, so __OR__
does not need to be modeled explicitly. __NOT__ is used for exclusion, while
intersections (__AND__) emerge through __combinatorics, nesting, and
normalization__ rather than as a separate operator. Restrictions or entity
bindings (__WITH__) do not require an explicit operator either, since they are
expressed __implicitly through tree structure and nesting__. This reduction to
a small set of constructs creates a __transparent, deterministic, and auditable
retrieval logic__ that can be easily integrated into existing NLP pipelines.

| Everyday sentence                        | Composer syntax          | Relational analogy        |
|------------------------------------------|--------------------------|---------------------------|
| Get something for A or B                 | `SET(A, B)`              | `WITH(A, B)`              |
| Get something for A and B                | `SET(A, B)`              | `WITH(A, B)`              |
| Get something for A and B, but not C     | `SET(A, B, NOT(C))`      | `WITH(A, B, NOT(C))`      |
| Get something for A or B, but not C      | `SET(A, B, NOT(C))`      | `WITH(A, B, NOT(C))`      |
| Get something for A, but not B and not C | `SET(A, NOT(B), NOT(C))` | `WITH(A, NOT(B), NOT(C))` |
| Get something for A or (B and C)         | `SET(A, B, C)`           | `WITH(A, B, C)`           | 

## Example

```
Text: "Get apples for the fruit cake, chocolate for the cookies, but no strawberries."
Entities: [
  {"label": "FRUITS", "text": "apples", "start": 4, "end": 10},
  {"label": "TREATS", "text": "fruit cake", "start": 19, "end": 29},
  {"label": "INGREDIENTS", "text": "chocolate", "start": 31, "end": 40},
  {"label": "TREATS", "text": "cookies", "start": 49, "end": 56},
  {"label": "FRUITS", "text": "strawberries", "start": 65, "end": 77}
]
```
_Semantic input from upstream components, e.g. Named Entity Recognition (NER)_

```
SET
+- SET
|  +- ENTITY (label:FRUITS, text:apples)
|  +- ENTITY (label:FRUITS, text:fruit cake)
+- SET
|  +- ENTITY (label:INGREDIENTS, text:chocolate)
|  +- ENTITY (label:TREATS, text:cookies)   
+- NOT
   +- ENTITY (label:FRUITS, text:strawberries)
```
_Tree representation of the return value (a node object)_

In the tree representation, the logical binding (e.g. _apples_ __with__ _fruit
cake_) -- or the logical grouping of _chocolate_ __and__ _cookies_ becomes
visible -- it arises implicitly through nesting, without the need for a separate
operator, and shows that the statement is much more than just `apples OR cake OR
    chocolate OR cookies`.

# Known Limitations

- __Focused expressiveness__  
  The logic layer is intentionally reduced to a small set of constructs: __SET__
  for grouping/relations and __NOT__ for exclusion. This ensures transparency
  and auditability, while more complex combinations (e.g., intersections) are
  expressed implicitly through nesting and normalization rather than as
  separate operators.
- __Language coverage__  
  Accuracy depends on the quality of syntactic parsing and the configured
  lexicons. Domain-specific terminology may require additional curation.
- __Context sensitivity__  
  The system operates on syntactic dependencies and lexical mappings. Semantic
  disambiguation (e.g. resolving polysemy such as _bank_ = "financial
  institution" vs. "bench") is outside the current scope.
- __Complementary role__  
  The approach is not designed to replace large language models. Instead, it
  provides a practical, interpretable foundation for retrieval and filtering
  tasks.
- __Scalability trade-offs__  
  Rule-based processing favors determinism and auditability, but may be less
  efficient than purely statistical or neural methods on very large datasets.

# Usage

# Benchmark

The benchmark tests were conducted on a system running Windows 11 with an Intel
Core i5-12400 and 16 GB of RAM. The templates used for evaluation included
conditional logic, loops, randomization, and annotated entities, representing a
moderately complex structure typical for synthetic text generation. The focus
was on measuring text throughput during large-scale data generation, excluding
I/O and external dependencies.

## Single-Pass Evaluation

## Scaled Evaluation (&times;500)

# API

The __relations__ module provides a compact API for parsing text with annotated
entities and constructing logical relation trees. It is suitable for semantic
preprocessing, retrieval pipelines, or rule-based reasoning workflows.

## Reference

### `sentences(lang: str, text: str) -> list[Sentence]`

<details>
  <summary>
Parse text into sentences using a Stanza NLP pipeline.
  </summary>

__Parameters__
- `lang (str)`: Language code (e.g. `"de"`, `"en"`).
- `text (str)`: Input text to be analyzed.

__Returns__
- `list[Sentence]`: A list of Stanza Sentence objects containing tokens, lemmas,
  POS tags, and dependency relations.

__Raises__
- `ValueError`: If the language code is missing or unsupported.
</details>

### `relations(lang: str, text: str, entities: list[tuple[int, int, str]], semantic: bool = True) -> Node`

<details>
  <summary>
Build a logical relation tree from text and annotated entities.
  </summary>

__Parameters__
- `lang (str)`: Language code (e.g. `"de"`, `"en"`).
- `text (str)`: Input text to be analyzed.
- `entities (list[tuple[int, int, str]])`: List of entity spans as
  `(start_index, end_index, label)`.
- `semantic (bool, optional)`: Controls how entities that occur multiple times
  on a level are handled.
  - If `True` (default), the equality of nodes is determined only by label and
    text of the contained entity. Multiple occurrences of entities at the same
    level are prevented. This produces a normalized, meaning-oriented relation
    tree.
  - If `False`, all occurrences of the entities are retained at the same level.
    This produces a form-oriented relation tree that reflects the original
    wording.

__Returns__
- `Node`: Root node of the relation tree (`NodeEmpty`, `NodeEntity`, `NodeSet`,
  `NodeNot`).

__Raises__
- `ValueError`: If the language code is missing or unsupported.
- `TypeError`: If input types are invalid.
</details>

### `pretty_print_sentence(sentence: Sentence) -> None`

<details>
  <summary>
Print a human-readable tree representation of a single parsed sentence.
  </summary>

__Parameters__
- `sentence (Sentence)`: A Stanza Sentence object.

__Raises__
- `TypeError`: If the input is not a `Sentence` instance.
</details>

### `pretty_print_sentences(sentences: list[Sentence]) -> None`

<details>
  <summary>
Print human-readable tree representations for a list of parsed sentences.
  </summary>

__Parameters__
- `sentences (list[Sentence])`: A list of Stanza Sentence objects.

__Raises__
- `TypeError`: If the input is not a list of `Sentence` instances or contains
  unsupported types.
</details>

### `pretty_print_node(node: Node) -> None`

<details>
  <summary>
Print a human-readable tree representation of a relation node.
  </summary>

__Parameters__
- `node (Node)`: The root node of the relation tree.

__Raises__
- `TypeError`: If the input is not a `Node` instance.
</details>

### `Entity`

Represents a recognized entity with label, text, and position.

### `Node`

Abstract base class for relation nodes.

### `NodeEmpty`

Empty node.

### `NodeEntity`

Single entity node.

### `NodeSet`

A set of entities or sub-nodes.

### `NodeNot`

Exclusion of the enclosed node.

# System Design

TODO:

# Concepts

- [Theoretische Ansätze](concepts.md#theoretische-ansätze)
  - [Allgemein](concepts.md#allgemein)
    - [Grundsatz](concepts.md#grundsatz)
    - [Syntaktische Konstituenten (Bausteine eines Satzes) als Cluster](
          concepts.md#syntaktische-konstituenten-bausteine-eines-satzes-als-cluster)
    - [Satzgrenzen als Gültigkeitsbereiche](
          concepts.md#satzgrenzen-als-gültigkeitsbereiche)
    - [Negation und Kontrast](concepts.md#negation-und-kontrast)
    - [Koreferenzauflösung / Coreference Resolution](
          concepts.md#koreferenzauflösung--coreference-resolution)
    - [Maximales Minimum](concepts.md#maximales-minimum)
  - [sprachspezifisch __`de`__](concepts.md#sprachspezifisch-de)
  - [sprachspezifisch __`dk`__](concepts.md#sprachspezifisch-dk)
  - [sprachspezifisch __`en`__](concepts.md#sprachspezifisch-en)
  - [sprachspezifisch __`es`__](concepts.md#sprachspezifisch-es)
  - [sprachspezifisch __`fr`__](concepts.md#sprachspezifisch-fr)
  - [sprachspezifisch __`it`__](concepts.md#sprachspezifisch-it)
  - [sprachspezifisch __`ru`__](concepts.md#sprachspezifisch-ru)
- [Test](#test)
  - [Bekannte Probleme](concepts.md#bekannte-probleme)
  - [Zielsetzung](concepts.md#zielsetzung)
  - [Vorgehensweise](concepts.md#vorgehensweise)
  - [Erweiterungen](concepts.md#erweiterungen)
  
TODO:  

# Sources & References
- https://stanfordnlp.github.io/stanza/neural_pipeline.html
- https://universaldependencies.org/docs/de/dep/
