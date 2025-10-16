# Introduction

Natural texts often contain terms that stand in implicit logical relationships
to one another -- for example, inclusion or exclusion relationships. The use of
modern AI systems for processing large amounts of data has shown that many
methods trained on general language usage, but without large language models,
can be too imprecise when applied to technical domain languages such as those
in industry, engineering and administration. This module addresses this issue:
it is intended to identify categorized terms and their relationships using
methods of natural language processing and to represent them in a transparent,
verifiable logical structure -- independently of large language models.
The resulting bridge between language and logic provides a foundation on which
existing AI systems can continue to build.

The module focuses on robust data structures and modular NLP pipelines. The
linguistic analysis is based on __[stanza](
    https://stanfordnlp.github.io/stanza/)__ with __[Universal Dependencies](
    https://universaldependencies.org/)__ and uses __dependency relations
(deprel)__ to capture syntactic dependencies more precisely.
These relations form the foundation for systematically identifying implicit
logical structures such as inclusion, exclusion, or nesting.

In addition, __language-specific keywords with logical meaning are taken from
configurable lexicons__, ensuring that the approach remains modular and can be
easily extended to additional languages.

Building on this, the __Semantic Logic Composer__ establishes a rule-based logic
layer, implementing the principles of __[Retrieval-Union Semantics (RUS)](
    #retrieval-union-semantics-rus)__ as described above. It processes entities
from upstream components and represents their relations using the basic
constructs __ANY__ (union) and __NOT__ (exclusion). Enumerations are always
interpreted as unions, making an explicit __OR__ unnecessary. An __AND__ in the
sense of an intersection does not exist; expressive power arises through
combination, nesting, and normalization. The resulting logical structure can be
expressed in __SQL, JSON, or YAML__ and serves downstream components as a
foundation for search or filtering.

This approach is __neither complete nor perfect__ and will __never replace a
large language model (LLM)__ -- natural language is simply too complex for
exhaustive coverage. Instead, it offers a __practical and extensible 
foundation__ for building __interpretable retrieval logic__.

# Features

# Table Of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Retrieval-Union Semantics (RUS)](#retrieval-union-semantics-rus)
- [Known Limitations](#known-limitations)
- [Usage](#usage)
- [Benchmark](#benchmark)
- [API Reference](#api-reference)
- [System Design](#system-design)
- [Sources & References](#sources--references)

# Retrieval-Union Semantics (RUS)

__Interpret logic in a retrieval-oriented manner, not in a formal-mathematical
manner.__

Retrieval-Union Semantics (RUS) is a minimalist yet complete model for
representing logical structures in retrieval tasks. Everything mentioned is
interpreted by default as a __union (ANY)__, so __OR__ does not need to be
modeled explicitly. __NOT__ is used for exclusion, while intersections (__AND__)
emerge through __combinatorics, nesting, and normalization__ rather than as a
separate operator. This reduction to a small set of primitives creates a
__transparent, deterministic, and auditable retrieval logic__ that can be easily
integrated into existing NLP pipelines.

| Everyday sentence                        | Composer syntax        | SQL equivalent          |
|------------------------------------------|------------------------|-------------------------|
| Get something for A or B                 | `ANY(A,B)`             | `(A OR B)`              |
| Get something for A and B                | `ANY(A,B)`             | `(A OR B)`              |
| Get something for A and B, but not C     | `ANY(A,B,NOT(C))`      | `(A OR B) AND NOT C`    |
| Get something for A or B, but not C      | `ANY(A,B,NOT(C))`      | `(A OR B) AND NOT C`    |
| Get something for A, but not B and not C | `ANY(A,NOT(B),NOT(C))` | `A AND NOT B AND NOT C` |
| Get something for A or (B and C)         | `ANY(A,B,C)`           | `A OR B OR C`           |

# Known Limitations

- __Focused expressiveness__  
  The logic layer is intentionally reduced to a small set of primitives __ANY__
  and __NOT__. This ensures transparency and auditability, while more complex
  constructs (e.g., explicit intersections) are represented through nesting and
  normalization.
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

# API Reference

# System Design

# Sources & References
- https://stanfordnlp.github.io/stanza/neural_pipeline.html
- https://universaldependencies.org/docs/de/dep/
