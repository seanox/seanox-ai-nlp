# Introduction

Natural-language input often contains implicit logical relations that are
difficult to capture in a structured and reproducible way. Phrases like
_"Compare A, B, and C but not D and E or F and G."_ encode nested combinations
of inclusion and exclusion, which are rarely made explicit in conventional
retrieval workflows.

The __Semantic Logic Composer__ provides a __rule-based__ approach to extracting
logical structures from semantic input. It operates on entities provided by
upstream components and represents their relations using the primitives __ANY__
(union) and __NOT__ (exclusion). Enumerations are always interpreted as unions,
so OR does not need to be modeled explicitly. An explicit __AND__ in the sense
of an intersection does not exist; __the expressiveness comes from combinatorics,
nesting, and normalization__. The resulting structure can be expressed in formats
such as SQL, JSON, or YAML, providing a basis that downstream components may use
for retrieval or filtering.

The module is intended as a lightweight component within an NLP pipeline. It
works independently of large language models (LLMs) and creates a transparent,
deterministic logical structure that downstream components can consume and
apply. Its design emphasizes auditability and adaptability, allowing
practitioners to control which entities are considered relevant and which are
explicitly excluded. The implementation relies on [stanza](
    https://stanfordnlp.github.io/stanza/) with [Universal Dependencies](
https://universaldependencies.org/) to create the structured entity
representations on which the Composer operates.

This approach is neither complete nor perfect and will never replace a large
language model (LLM) -- natural language is simply too complex for exhaustive
coverage. Instead, it offers a practical and extensible foundation for building
interpretable retrieval logic.

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

Retrieval-Union Semantics (RUS) is a minimalist yet complete model for
representing logical structures in retrieval tasks. Everything mentioned is
interpreted by default as a __union (ANY)__, so __OR__ does not need to be
modeled explicitly. __NOT__ is used for exclusion, while intersections (__AND__)
emerge through __combinatorics, nesting, and normalization__ rather than as a
separate operator. This reduction to a small set of primitives creates a
__transparent, deterministic, and auditable retrieval logic__ that can be easily
integrated into existing NLP pipelines.

__Interpret logic in a retrieval-oriented manner, not in a formal-mathematical
manner.__

| Everyday sentence                        | Composer syntax        | SQL equivalent          |
|------------------------------------------|------------------------|-------------------------|
| Get something for A or B                 | `ANY(A,B)`             | `(A OR B)`              |
| Get something for A and B                | `ANY(A,B)`             | `(A OR B)`              |
| Get something for A and B, but not C     | `ANY(A,B,NOT(C))`      | `(A OR B) AND NOT C`    |
| Get something for A or B, but not C      | `ANY(A,B,NOT(C))`      | `(A OR B) AND NOT C`    |
| Get something for A, but not B and not C | `ANY(A,NOT(B),NOT(C))` | `A AND NOT B AND NOT C` |
| Get something for A or (B and C)         | `ANY(A,B,C)`           | `A OR B OR C)`          |

# Known Limitations

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
