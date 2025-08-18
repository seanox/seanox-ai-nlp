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

# Template

## Schema

```Yaml
templates:
  - name: <string>             # Unique identifier for the template
    condition: <expression>    # Optional condition to activate the template
    template: <string>         # Sentence with annotated placeholders
    spans:                     # Optional: custom span definitions
      - label: <string>        # Name of the span (e.g. "planet", "moon")
        regex: <string>        # Regex pattern to extract the span
```

## Field Details
- __name__: A unique identifier for the template, used for referencing and
  debugging.
- __condition__: A string representing a logical expression. It must evaluate to
  `True` for the template to be used. Example: `planet != "Earth"`.
- __template__: A sentence string containing placeholders, expressions,
  functions, and optional annotations via (`annotate`).
- __spans__:
  - Each span defines a __label__ and a __regex__ pattern.
  - The span's position is determined by the full match of the regular
    expression -- from the start to the end of the match.
  - Useful for extracting relationships or nested entities not covered by inline
    annotations (`annotate`).

## Additional Jinja2 filters

### `annotate(value: Any, label: str = "") -> str`

<details>
  <summary>
Marks a value with a structured entity label for downstream processing (e.g.
entity extraction).
  </summary>

```
{{ value | annotate("LABEL") }}
produce: [[[LABEL]]]value[[[-]]]
```

__Parmeters__:
- `value (Any)`: The value to annotate. Will be converted to a string.
- `label (str)`: The entity label to apply. The same conventions apply as for
   variable names. In addition, the minus sign is permitted between word
   characters.

__Returns__:
- `str`: The annotated string if the label is valid, otherwise the original
  value.

__Behavior__
- Wraps the string representation of `value` with custom entity markers.
- Returns the original value if the label is invalid or empty.

__Purpose__
Enables inline annotation of entities in generated text.
</details>

### `random_range(items: list[Any], limit: int = -1) -> list[Any]`

<details>
  <summary>
Randomly selects and shuffles a subset of items from the provided list.
  </summary>

```
{{ random_range(["apple", "banana", "cherry"], 2) }}
might return: ["banana", "apple"]
```

__Parameters__:
- `items (list[Any])`: The list of items to choose from.
- `limit (int)`: Maximum number of items to include. If negative, all items are
  considered.

__Returns__:
- `list[Any]`: A randomly selected and shuffled subset of the input list.

__Behavior__:
- Picks between 1 and `limit` items from the list.
- Shuffles the result before returning.
- Returns an empty list if input is empty or limit is zero.

__Purpose__:
Provides controlled variation in template-generated content.
</details>

### `random_range_join(items: list[Any], separator: str = ", ", limit: int = -1) -> str`

<details>
  <summary>
Randomly selects and joins a subset of items into a single string.
  </summary>

```
{{ ["apple", "banana", "cherry"] | random_range_join(",", 2) }}
might produce: "cherry, apple"
```

__Parameters__:
- `items (list[Any])`: List of strings to choose from.
- `separator (str)`: Separator used between selected items.
- `limit (int)`: Maximum number of items to include. If negative, all items are
  considered.

__Returns__:
- `str`: Joined string of randomly selected items, or an empty string if input
  is empty.

__Behavior__:
- Selects between 1 and `limit` items from the list.
- Shuffles the selection and joins it using the specified separator.
- Returns an empty string if the input list is empty.

__Purpose__:
Generates dynamic, varied list expressions for use in template-generated text.
</details>

### `random_range_join_phrase(items: list[Any], separator: str = ", ", word: str = ", ", limit: int = -1) -> str`

<details>
  <summary>
Randomly selects and joins items into a natural-language phrase.
  </summary>

```
{{ items | random_range_join_phrase(", ", " and ", 3) }}
might produce: "banana, cherry and apple"
```

__Parameters__:
- `items (list[Any])`: List of strings to choose from.
- `separator (str)`: Separator used between items before the final one.
- `word (str)`: Conjunction word before the last item (e.g., `"and"`, `"or"`).
- `limit (int)`: Maximum number of items to include. If negative, all items are
  considered.

__Returns__:
- `str`: Natural-language phrase of randomly selected items, or an empty string if input is empty.

__Behavior__:
- Selects between 1 and `limit` items from the list.
- Shuffles the selection and formats it as:
  - One item → returned as-is.
  - Two items → joined with the conjunction word.
  - Three or more → joined with separator, and the last item prefixed by the conjunction word.

__Purpose__:
Creates human-friendly phrases for use in template-generated text, ideal for lists in natural language.
</details>

### `random_set(items: list[Any], count: int = -1) -> list[Any]`

<details>
  <summary>
Randomly selects a subset of items from a list.
  </summary>

```
{{ ["apple", "banana", "cherry"] | random_set(2) }}
might return: ["banana", "apple"]
```

__Parameters__:
- `items (list[Any])`: List of items to choose from.
- `count (int)`: Number of items to select. If negative or exceeds list length,
  all items are returned in random order.

__Returns__:
- `list[Any]`: A randomly selected subset of items, or an empty list if input is
  empty.

__Behavior__:
- Returns up to `count` randomly selected items.
- If `count` is negative → returns all items in random order.
- If `count` is zero or list is empty → returns an empty list.

__Purpose__:
Provides raw access to a randomized subset of items for further use in templates or logic.
</details>

## Example Template File
See a working example in [synthetics_en_annotate.yaml](
    ../../tests/synthetics_en_annotate.yaml)

# System Design

TODO

## Components Overview

TODO

## Processing Workflow

TODO

# Known Limitations

None are known at this time.

# Usage

```python
from seanox_ai_nlp.synthetics import synthetics
import json

with open("synthetics-planets_en.json", encoding="utf-8") as file:
  datas = json.load(file)

for data in datas:
  synthetic = synthetics(".", "en_annotate", data)
  print(synthetic)
```

Example Output:
```
Synthetic(
    text='Closest planet to the Sun as well as Many impact craters are characteristic of Mercury.',
    annotation='[[[characteristics]]]Closest planet to the Sun[[[-]]] as well as [[[characteristics]]]Many impact craters[[[-]]] are characteristic of [[[planet]]]Mercury[[[-]]].',
    entities=[
        (0, 25, 'characteristics'),
        (37, 56, 'characteristics'),
        (79, 86, 'planet')
    ],
    spans=[]
),
Synthetic(
    text="'planet: Earth', 'type: terrestrial planet', 'diameter: 12742', ...",
    annotation="'[[[terms]]]planet[[[-]]]: [[[planet]]]Earth[[[-]]]', ...",
    entities=[
        (1, 7, 'terms'),
        (9, 14, 'planet'),
        ...
    ],
    spans=[
        (1, 14, 'PAIR'),
        (18, 42, 'PAIR'),
        ...
    ]
),
...
```

## Integration in NLP-Workflows

TODO

## Downstream Processing with pandas

```
from seanox_ai_nlp.synthetics import synthetics
import json
import pandas

LABEL_COLORS = {
    "planet": ("\033[38;5;0m", "\033[48;5;117m"),   # white on blue
    "term":   ("\033[38;5;0m", "\033[48;5;250m")    # black on light gray
}

def highlight_entities(text, entities):
    reset = '\033[0m'
    for start, end, label in sorted(entities, key=lambda x: -x[0]):
        if label not in LABEL_COLORS:
            label = "term"
        fg, bg = LABEL_COLORS[label]
        colored = f"{fg}{bg}{text[start:end]}{reset}"
        text = text[:start] + colored + text[end:]
    return text

# Load synthetic input data
with open("synthetics-planets_en.json", encoding="utf-8") as file:
    datas = json.load(file)

# Generate color-coded output for terms and planets
for data in datas:
    synthetic = synthetics(".", "en_annotate", data)
    print(highlight_entities(synthetic.text, synthetic.entities))
    
    dataframe = pandas.DataFrame(synthetic.entities, columns=["start", "end", "label"])
    dataframe["text"] = dataframe.apply(lambda row: synthetic.text[row["start"]:row["end"]], axis=1)
    dataframe = dataframe[["start", "end", "label", "text"]]
    print(dataframe.to_string(index=False))    
```

Example Output:
```
Compared to Earth, Mars takes 322 more days to complete its orbit.
 start  end    label          text
    12   17     term         Earth
    19   23   planet          Mars
    30   43 turnover 322 more days
    60   65     term         orbit
```

# Benchmark

The module was tested on an Intel Core i5-12400 with 16 GB RAM running Windows 11.

## Single-Pass Evaluation

[test_synthetics_benchmark_01](../../tests/test_synthetics_synthetics.py)

| Metric                         | Value              |
|--------------------------------|--------------------|
| Varied text without repetition | 1,813 characters   |
| Iterations                     | 8 x                |
| Processing time                | 0.94 ms            |
| Avg. time per iteration        | ~0.1175 ms         |
| Theoretical throughput         | ~1,928,723 chars/s |

## Scaled Evaluation (&times;500)

[test_synthetics_benchmark_02](../../tests/test_synthetics_synthetics.py)

| Metric                               | Value              |
|--------------------------------------|--------------------|
| Scaled Data (500&times; single test) | 848,888 characters |
| Iterations                           | 4000 x             |
| Processing time                      | 346.10 ms          |
| Avg. time per iteration              | ~0.0865 ms         |
| Theoretical throughput               | ~2,452,724 chars/s |

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

## `TemplateSyntxException`

Raised when a syntax error occurs in the jinja2 template.

# Sources & References

- https://jinja.palletsprojects.com/en/stable/
