<p>
  <a href="https://github.com/seanox/seanox-ai-nlp/pulls"
      title="Development"
    ><img src="https://img.shields.io/badge/development-active-green?style=for-the-badge"
  ></a>  
  <a href="https://github.com/seanox/seanox-ai-nlp/issues"
    ><img src="https://img.shields.io/badge/maintenance-active-green?style=for-the-badge"
  ></a>
  <a href="https://seanox.com/contact"
    ><img src="https://img.shields.io/badge/support-active-green?style=for-the-badge"
  ></a>
</p>

# Description
Structured data in technical domains (e.g. engineering, meteorology) often
contain specialized terminology, measurement units, parameter specifications,
and symbolic values. These elements pose challenges for embedding-based
similarity methods due to limited semantic resolution.

This package follows a hybrid approach that combines rule-based processing with
NLP-based filtering. It does not rely on embedding-based retrieval methods.
Instead, it explicitly identifies domain-specific entities and organizes them
across multiple abstraction levels to support interpretable and reproducible
retrieval workflows.

The system integrates lightweight components into existing NLP pipelines. These
components operate without dependence on non-transparent large language models
(LLMs) and are designed to structure semantically relevant data based on
deterministic and auditable mechanisms.

__Additional modules are planned to support structured query generation,
including:__

- __Logic Query Composer__: Parses natural-language input and produces a logical
 structure enriched with extracted entities, which can serve as a basis for
 formats like SQL, JSON or YAML.

__Example Pipeline: Structured NLP Workflow__

```mermaid
---
config:
  theme: neutral
---
flowchart TD
    subgraph Feedback Loop 
        K[New Data + Natural-language Query] --> L[Synthetics Updates]
        L --> L1[synthetics + units]
        L1 --> M[NLP Component Update]
    end
    subgraph Retrieval Process
        D[Natural-language Query] --> E[Entity Extraction]
        E --> [Semantic and Logical Analysis]
        E --> E1[logic query composer]
        E1 --> F[Logical Structure]
        F --> G[Manual SQL Composition]
        G --> H[SQL]
        H --> I[Database Execution]
        I --> J[Retrieval]
    end
    subgraph Training Pipeline
        A[Structured Data] --> B[Synthetic Annotated Sentences]
        B --> B1 [synthetics + units]
        B1 --> C[NLP Component Update]
    end
```

> [!NOTE] 
> __NLP Component__ refers to configurable elements within the pipeline,
> including rule-based extractors, template-driven generators, and optionally
> small-scale NLP models (e.g. spaCy pipelines). These components are
> transparent, auditable, and do not rely on large language models (LLMs).

# Licence Agreement
Seanox Software Solutions is an open-source project, hereinafter referred to as
__Seanox__.

This software is licensed under the __Apache License, Version 2.0__.

__Copyright (C) 2025 Seanox Software Solutions__

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at

https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.

# System Requirement
- Python 3.9 or higher

# Installation & Setup
```
pip install seanox-ai-nlp
```

# Packages & Modules

## [units](https://github.com/seanox/seanox-ai-nlp/blob/master/seanox_ai_nlp/units/README.md)
The `units` module applies rule-based, deterministic pattern recognition to
identify numerical expressions and measurement units in text. It is designed for
integration into lightweight NLP pipelines and does not rely on large language
models (LLMs). Its language-agnostic architecture and flexible formatting
support a broad range of use cases, including general, semi-technical, and
semi-academic content.

The module can be integrated with tools such as spaCy’s `EntityRuler`, enabling
annotation, filtering, and token alignment workflows. It produces structured
output suitable for downstream semantic analysis, without performing semantic
interpretation itself.

### Features
- __Pattern-based extraction__  
  Identifies constructs like _5 km_, _-20 &ordm;C_, or _1000 hPa_ using regular
  expressions and token patterns -- no training required.

- __Language-independent architecture__  
  Operates at token and character level, making it effective across multilingual
  content.

- __Support for compound expressions__  
  Recognizes unit combinations (_km/h, kWh/m&sup2;, g/cm&sup3;_) and numerical
  constructs nvolving signs and operators: _&plusmn;, &times;, &middot;,
  :, /, ^, –_ and more.

- __Integration-ready output__  
  Returns structured entities compatible with tools like spaCy’s EntityRuler for
  use in rule-based NLP pipelines.

### Quickstart
```python
from seanox_ai_nlp.units import units
text = "The cruising speed of the Boeing 747 is approximately 900 km/h (559 mph)."
for entity in units(text):
    print(entity)
```

- [Usage](https://github.com/seanox/seanox-ai-nlp/blob/master/seanox_ai_nlp/units/README.md#usage)
- [Integration in NLP Workflows](https://github.com/seanox/seanox-ai-nlp/blob/master/seanox_ai_nlp/units/README.md#integration-in-nlp-workflows)
- [Downstream Processing with pandas](https://github.com/seanox/seanox-ai-nlp/blob/master/seanox_ai_nlp/units/README.md#downstream-processing-with-pandas)

## [synthetics](https://github.com/seanox/seanox-ai-nlp/blob/master/seanox_ai_nlp/synthetics/README.md)
The __synthetics__ module generates annotated natural language from
domain-specific, structured input data -- such as records from databases or
knowledge graphs. It uses template-based, rule-driven methods to produce
linguistically rich and semantically annotated sentences. Designed for
controlled NLP pipelines, it avoids large language models (LLMs) and instead
supports deterministic, auditable generation. Through stochastic variation and
semantic recombination, it enables fine-tuning, evaluation, and data
augmentation -- without performing semantic interpretation.

### Features
- __Template-Based Text Generation__  
  Generates controlled content in natural language from structured input using
  YAML-defined Jinja2 templates. Template selection is context-sensitive based
  on input attributes.
- 
- __Stochastic Variation__  
  Built-in filters like __random_set__, __random_range__, __random_range_join__
  and __random_range_join_phrase__ introduce lexical and syntactic diversity
  from identical data structures.

- __Domain-Specific Annotation__  
  Annotates entities with structured markers for precise extraction and
  fine-grained control over type and placement.

- __Rule-Based Span Detection__  
  Identifies semantic spans using regular expressions, independent of
  tokenization or linguistic parsing.

- __Interpretation-Free Generation__  
  Deterministic output without semantic analysis; compatible with reproducible
  and auditable workflows.

- __NLP Pipeline Compatibility__  
  The `Synthetic` object includes raw text, annotated text, entity spans with
  labels and positions, and regex-based semantic spans. Compatible with
  spaCy-style frameworks for fine-tuning, evaluation, and augmentation.

### Quickstart
TODO:

# Changes
## 1.0.0 20250808
NT: Release is available

[Read more](https://raw.githubusercontent.com/seanox/seanox-ai-nlp/refs/heads/master/CHANGES)

# Contact
[Issues](https://github.com/seanox/seanox-ai-nlp/issues)  
[Requests](https://github.com/seanox/seanox-ai-nlp/pulls)  
[Mail](https://seanox.com/contact)
