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
components operate independently of large language models (LLMs) and are
designed to structure relevant data using deterministic and auditable
mechanisms.

__Additional modules are planned to support structured query generation,
including:__

- __Logic Query Composer__: Parses natural-language input and produces a logical
  structure enriched with extracted entities. This structure can be used as a
  basis for formats such as SQL, JSON or YAML.

__Example Pipeline: Structured NLP Workflow__

```mermaid
---
config:
  theme: neutral
---
flowchart TD
    subgraph subGraph3["Feedback Loop (optional)"]
        L["New Data + Natural-language Query"]
        subgraph subGraph3-1["synthetics + units"]
            M["Synthetics Updates"]
        end
        N["NLP Component Update"]
    end
    subgraph subGraph2["Retrieval Process"]
        D["Natural-language Query"]
        E["Entity Extraction"]
        subgraph subGraph2-1["logic query composer"]
            F["Semantic and Logical Analysis"]
        end
        G["Logical Structure"]
        H["Manual SQL Composition"]
        I["SQL"]
        J["Database Execution"]
        K["Retrieval"]
    end
    subgraph subGraph1["Training Pipeline"]
        A["Structured Data"]
        subgraph subGraph1-1["synthetics + units"]
            B["Synthetic Annotated Sentences"]
        end
        C["NLP Component Update"]
    end
    A --> B
    B --> C
    D --> E
    E --> F
    F --> G
    G --> H
    H --> I
    I --> J
    J --> K
    L --> M
    M --> N
    style subGraph1-1 fill:#BBDEFB
    style subGraph2-1 fill:#BBDEFB
    style subGraph3-1 fill:#BBDEFB
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
The __units__ module applies rule-based, deterministic pattern recognition to
identify numerical expressions and measurement units in text. It is designed for
integration into lightweight NLP pipelines and does not rely on large language
models (LLMs). Its language-agnostic architecture and flexible formatting
support a broad range of use cases, including general, semi-technical and
semi-academic content.

The module can be integrated with tools such as spaCy’s `EntityRuler`, enabling
annotation, filtering, and token alignment workflows. It produces structured
output suitable for downstream analysis, without performing semantic
interpretation.

### Features
- __Pattern-based extraction__  
  Identifies constructs like _5 km_, _-20 &ordm;C_, or _1000 hPa_ using regular
  expressions and token patterns -- no training required.
- __Language-independent architecture__  
  Operates at token and character level; applicable across multilingual content.
- __Support for compound expressions__  
  Recognizes unit combinations (_km/h, kWh/m&sup2;, g/cm&sup3;_) and numerical
  constructs involving signs and operators: _&plusmn;, &times;, &middot;,
  :, /, ^, –_ and more.
- __Integration-ready output__  
  Returns structured entities compatible with tools like spaCy’s EntityRuler.

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
The __synthetics__ module generates annotated natural language from structured
input data -- such as records from databases or knowledge graphs. It uses
template-based, rule-driven methods to produce controlled and annotated
sentences. Designed for deterministic NLP pipelines, it avoids large language
models (LLMs) and supports reproducible generation.

### Features
- __Template-Based Text Generation__  
  Produces natural-language output from structured input using YAML-defined
  Jinja2 templates. Template selection is context-sensitive.
- __Stochastic Variation__  
  Filters such as __random_set__, __random_range__, and
- __random_range_join_phrase__ introduce lexical and syntactic diversity from
  identical data structures.
- __Domain-Specific Annotation__  
  Annotates entities with structured markers for precise extraction and control.
- __Rule-Based Span Detection__  
  Identifies semantic spans using regular expressions, independent of
  tokenization or parsing.
- __Interpretation-Free Generation__  
  Output is deterministic and reproducible; no semantic analysis is performed.
- __NLP Pipeline compatibility__  
  The __Synthetic__ object includes raw and annotated text, entity spans and
  regex-based semantic spans. Compatible with spaCy-style frameworks for
  fine-tuning, evaluation, and augmentation.

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
