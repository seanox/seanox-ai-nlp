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
__Working with structured, domain-specific data__ presents a persistent
challenge for semantic alignment in NLP pipelines. Embedding-based similarity in
__Retrieval-Augmented Generation (RAG)__ systems often fails to adequately
capture the nuanced semantics these data entail -- such as technical units in
industrial contexts, product specifications in e-commerce, clinical lab values
in medical records, or meteorological parameters like wind direction and UV
index. 

This package concentrates on a __hybrid approach__ that combines __rule-based__
processing with __NLP-driven preselection__. The core idea is that __semantic
matching__ can be improved when domain-specific entities are identified and made
available across multiple levels of abstraction. By simplifying the provision
and detection of these entities, the package can enhance the
__interpretability__ and __precision of__ retrieval workflows.

The approach combines:

- __Token-sensitive preprocessing__ for better contextual understanding
- __Rule-based enhancements__ to detect technical terms and units
- __Modular components__ that integrate easily into existing retrieval systems

The package can contribute to __narrowing the gap__ between structured data and
semantically rich queries by supporting existing NLP workflows with lightweight
components tailored for domain-specific terminology and semantic matching --
without relying on opaque models or extensive training.

Further modules are planned to extend the package's capabilities, including:

- __Logic Query Composer__: For transforming natural-language queries into
  structured formats (e.g. SQL, JSON, YAML, etc.)

# Licence Agreement
LIZENZBEDINGUNGEN - Seanox Software Solutions ist ein Open-Source-Projekt, im
Folgenden Seanox Software Solutions oder kurz Seanox genannt.

Diese Software unterliegt der Version 2 der Apache License.

Copyright (C) 2025 Seanox Software Solutions

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
The units module uses __rule-based__, __deterministic pattern recognition__ to
identify numerical expressions and units in text. It does not rely on __large
language models (LLMs)__ and is suitable for integration into __lightweight NLP
pipelines__. Its language-agnostic design and adaptable formatting support a
wide range of applications, including general, semi-technical, and semi-academic
content. The module can be integrated with tools like spaCy’s __EntityRuler__,
supporting __annotation__, __filtering__, and __token alignment__ workflows with
structured output for downstream semantic analysis -- without performing it
itself.

### Features
- __Pattern-based extraction__  
  Identifies constructs like _5 km_, _-20 &ordm;C_, or _1000 hPa_ using regular
  expressions and token patterns -- no training required.
  
- __Language-independent architecture__  
  Operates at token and character level, making it effective across multilingual
  content.
  
- __Support for compound expressions__  
  Recognizes both unit combinations (_km/h, kWh/m&sup2;, g/cm&sup3;_) and
  numerical constructs using signs and operators: _&plusmn;, &times;, &middot;,
  :, /, ^, –_ and more.
  
- __Integration-ready output__  
  Returns structured results compatible with tools like spaCy’s EntityRuler for
  use in pipelines.
  
- __Transparent design__  
  Fully interpretable and deterministic -- avoids black-box ML, supporting
  reliable and auditable processing.

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

The __synthetics__ module uses __template-based__, __rule-driven generation__ to
transform structured domain data into annotated natural language. It does not
rely on __large language models (LLMs)__ and is designed for use in
__controlled, domain-specific NLP pipelines__. Through __stochastic variation__
and __semantic recombination__, it produces linguistically rich sentences from
precise input. The module supports __fine-tuning__, __evaluation__, and __data
augmentation__ workflows by enhancing semantic coverage and contextual
adaptability -- without performing interpretation itself.

### Features

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
