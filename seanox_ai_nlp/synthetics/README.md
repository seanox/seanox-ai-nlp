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
  __random_range__, __random_range_join__, __random_range_join_phrase__ and
  __random_set__ allowing the generation of semantically varied sentences from
  identical data structures.

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
  The output object __Synthetic__ includes raw text, annotated text, entity
  spans with labels and positions, and regex-based semantic spans. This
  structure supports fine-tuning, evaluation, and data augmentation in
  domain-specific NLP pipelines, including spaCy-style frameworks.

# Table Of Contents

- [Introduction](#introduction)
- [Features](#features)

TODO
TODO Where to put the template documentation (structure, syntax, functions)?

# System Design

The __synthetics__ module is built around a template-driven generation engine
using __Jinja2__. Templates are defined in YAML files and selected based on
input conditions.

The system architecture includes:

- __Template Loader__
  Loads language-specific YAML files and compiles templates with conditions.

- __Filter Registration__  
  Custom Jinja2 filters (__annotate__, __random_range__, __random_set__ etc.)
  enable stochastic variation and entity tagging.

- __Syntax & Condition Validation__  
  Before any template is used, both its syntax and condition logic are
  validated:
  - Templates are compiled using Jinja2 to ensure renderability.
  - Conditions are checked for unsafe tokens and tested for syntactic correctness.
  - Invalid or unrenderable templates are excluded during initialization.

- __Caching Layer__  
  Templates are cached in-memory to optimize repeated generation calls.

- __Entity Extraction__  
  Annotated output is parsed using regex to extract entity spans and semantic
  patterns.

- __Output Structure__
  The result is encapsulated in a __Synthetic__ object, containing raw text,
  annotated text, entity metadata, and span matches.

This design ensures deterministic, interpretable, and domain-adaptable synthetic
text generation for NLP workflows.

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

## `synthetics(datasource: str, language: str, data: dict[str, Any]) -> Synthetic`

<details>
  <summary>
Generates synthetic text using predefined YAML templates.

The function loads templates from a language-specific YAML file (e.g.
'synthetics_en.yaml'), evaluates conditions associated with each template,
randomly selects one of the matching entries, and renders it using Jinja2.
  </summary>

Templates are cached internally to improve performance on repeated invocations.

__Parameters:__
- `datasource (str)`: Path to the directory containing the YAML template files.
- `language (str or Enum)`: Language identifier used to select the correct
  template file.
- `data (dict)`: Contextual data used to evaluate conditions and render the
  template.

__Returns:__
- `Synthetic`: A dataclass containing the generated synthetic text, its 
  annotated version, and metadata about entities and spans.

__Raises:__
- `FileNotFoundError`: If the YAML template file for the given language cannot
  be found at the specified path.
- `TemplateException`: If the template file cannot be loaded or parsed.
- `TemplateConditionException`: If a condition expression in the template is
  invalid or unsafe to evaluate.
</details>

## `Synthetic`

TODO

## `TemplateException`

Raised when the template file cannot be loaded or parsed due to general errors
in the YAML.

## `TemplateConditionException`

Raised when a condition expression in the template is invalid or unsafe to
evaluate.

# Sources & References

TODO
