# Introduction

Processing structured data with NLP models in domain-specific contexts -- such
as industry, e-commerce, medicine, or meteorology -- remains challenging. Models
trained on general corpora often struggle to interpret specialized terminology
correctly or place it in the appropriate semantic context. Structured data is
typically precise but lacks linguistic form and semantic depth, which limits its
usefulness for tasks like natural language generation and semantic retrieval.

Synthetic sentences with annotated domain-specific content offer a way to make
structured input linguistically more accessible. By recombining lexical,
syntactic, and semantic elements in a controlled manner, these sentences
introduce systematic variation. This can help to broaden semantic coverage and
supports the adaptation of models to specific domains.

The __synthetics__ module provides a generator based on templates and
transformation rules. It introduces variation through stochastic selection and
controlled recombination, producing annotated sentences from structured input.
These outputs can be used to create training data for fine-tuning, evaluation,
or augmentation in domain-specific NLP workflows.

# Features

- __Template-Based Text Generation__  
  The module uses YAML-defined templates with Jinja2 syntax to generate
  controlled natural language from structured input. It supports conditional
  template selection based on input attributes, enabling flexible and
  context-sensitive generation.

- __Stochastic Variation__  
  Lexical and syntactic diversity is introduced through built-in filters such as
  __random_join__, __random_set__, and __random_join_phrase__, allowing the
  generation of semantically varied sentences from identical data structures.

- __Domain-Specific Annotation__  
  Entities are annotated using structured markers which facilitates precise
  extraction and provides fine-grained control over entity types and their
  placement within the text.

- __Rule-Based Span Detection__  
  The module applies regular expressions to identify semantic spans in annotated
  text, enabling the definition of complex patterns independently of
  tokenization or linguistic parsing.

- __Interpretation-Free Generation__  
  No semantic interpretation or analysis is performed during generation,
  ensuring that the output remains deterministic, transparent, and suitable for
  controlled NLP workflows.

- __Compatibility with NLP Workflows__  
  The output object __SyntheticResult__ includes raw text, annotated text,
  entity spans with labels and positions, and regex-based semantic spans. This
  structure supports fine-tuning, evaluation, and data augmentation in
  domain-specific NLP pipelines, including spaCy-style frameworks.

# Table Of Contents

- [Introduction](#introduction)
- [Features](#features)

TODO
TODO Where to put the template documentation (structure, syntax, functions)?

# Technical Architecture

TODO

## Components Overview

TODO

## Processing Workflow

TODO

## Data Management

TODO

# Known Limitations

TODO

# Usage

TODO

## Integration in NLP-Workflows

TODO

## Downstream Processing with pandas

TODO

# Benchmark

TODO

## Single-Pass Evaluation

TODO

## Scaled Evaluation (&times;10)

TODO

# API Reference

TODO

# Sources & References

TODO