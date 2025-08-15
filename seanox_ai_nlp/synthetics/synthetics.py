# seanox_ai_npl/synthetics/synthetics.py

from jinja2 import Environment, BaseLoader
from typing import Any
from dataclasses import dataclass

import os
import random
import re
import yaml


def _re_compile(expression: str, debug: bool = False) -> re.Pattern:
    expression = re.sub(r"\s{2,}|[\r\n]+", "", expression)
    if not debug:
        return re.compile(expression)
    return expression


def _re_unnamed_groups(expression: str) -> str:
    return re.sub(r"\(\?P<[^>]+>", "(?:", expression)


_ENTITY_MARKER_SIGNATURE_START = "[[["
_ENTITY_MARKER_SIGNATURE_END = "]]]"

_ENTITY_MARKER_NAME_RAW_PATTERN = r"\w(?:[\w\-]*\w)?"
_ENTITY_MARKER_START_RAW_PATTERN = rf"""
    (?:
        {re.escape(_ENTITY_MARKER_SIGNATURE_START)}
        (?P<entity_label>{_ENTITY_MARKER_NAME_RAW_PATTERN})
        {re.escape(_ENTITY_MARKER_SIGNATURE_END)}
    )
"""
_ENTITY_MARKER_END_RAW_PATTERN = rf"""
    (?:
        {re.escape(_ENTITY_MARKER_SIGNATURE_START)}
        (?:-)
        {re.escape(_ENTITY_MARKER_SIGNATURE_END)}
    )
"""
_ENTITY_MARKER_RAW_PATTERN = rf"""
    (?P<entity_start_tag>{_ENTITY_MARKER_START_RAW_PATTERN})
    (?P<entity_intermediate_text>.*?)
    (?P<entity_end_tag>{_ENTITY_MARKER_END_RAW_PATTERN})
"""
# TODO Test edge cases and clarify whether this is necessary
_ENTITY_MARKER_SPACE_PATTERN = [
    #    _re_compile(rf"""
    #        (?P<entity_space_prefix>
    #          {_re_unnamed_groups(_ENTITY_MARKER_START_RAW_PATTERN)}
    #          .*?
    #          {_re_unnamed_groups(_ENTITY_MARKER_END_RAW_PATTERN)})
    #        (?P<entity_space_suffix>[\.\,\:/])
    #    """),
    #    _re_compile(rf"""
    #        (?P<entity_space_prefix>[\)\]\s]/)
    #        (?P<entity_space_suffix>{_re_unnamed_groups(_ENTITY_MARKER_START_RAW_PATTERN)})
    #    """),
    #    _re_compile(rf"""
    #        (?P<entity_space_prefix>{_re_unnamed_groups(_ENTITY_MARKER_END_RAW_PATTERN)})
    #        (?P<entity_space_suffix>[\)\]\"\'])
    #    """)
]

_ENTITY_MARKER_NAME_PATTERN = re.compile(rf"^{_ENTITY_MARKER_NAME_RAW_PATTERN}$")
_ENTITY_MARKER_PATTERN = _re_compile(_ENTITY_MARKER_RAW_PATTERN)


def _annotate(value: Any, label: str = "") -> str:
    """
    The method is intended as a function in the template and annotates a given
    value with a structured entity marker if a valid label is provided.

    Designed for use as a Jinja2 filter. This function wraps the string
    representation of `value` with a custom marker format that includes the
    entity label. The format is designed for downstream processing, such as
    entity extraction.

    If the label is invalid or empty, the original value is returned unchanged.

    Example:
        {{ value | annotate("VALUE") }}
        produce: [[[VALUE]]]value[[[-]]]

    Args:
        value (Any): The value to annotate. Will be converted to a string.
        label (str): The entity label to apply. The same conventions apply as
            for variable names. In addition, the minus sign is permitted between
            word characters.

    Returns:
        str: The annotated string if the label is valid, otherwise the original
            value.
    """
    value = str(value)
    if not label or not _ENTITY_MARKER_NAME_PATTERN.match(label.strip()):
        return value
    return (
        f"{_ENTITY_MARKER_SIGNATURE_START}"
        f"{label.strip()}"
        f"{_ENTITY_MARKER_SIGNATURE_END}"
        f"{value}"
        f"{_ENTITY_MARKER_SIGNATURE_START}"
        f"-"
        f"{_ENTITY_MARKER_SIGNATURE_END}"
    )


def _random_join(items: list[str], separator: str, limit: int = -1) -> str:
    """
    The method is intended as a function in the template. It randomly selects
    and joins a subset of strings from the provided list using the given
    separator.

    Designed for use as a Jinja2 filter. This function picks a random number of
    items (between 1 and `limit` or the length of `items`) from the input list,
    shuffles them, and joins them into a single string using the specified
    separator.

    If the list is empty, an empty string is returned. If `limit` is negative,
    all items are considered.

    Example:
        {{ ["apple", "banana", "cherry"] | random_join(",", 2) }}
        might produce: "cherry, apple"

    Args:
        items (list[str]): The list of strings to choose from.
        separator (str): The string used to separate the selected items.
        limit (int, optional): Maximum number of items to include. If negative,
            no limit is applied.

    Returns:
        str: A string of randomly selected and joined items, or an empty string
            if `items` is empty.
    """
    if not items:
        return ""
    max_items = len(items)
    if limit >= 0:
        max_items = min(limit, len(items))
    count = random.randint(1, max_items)
    selection = random.sample(items, count)
    random.shuffle(selection)
    return separator.join(selection)


def _random_join_phrase(items: list[str], separator: str, word: str, limit: int = -1) -> str:
    """
    The method is intended as a function in the template. It randomly selects
    and joins a subset of strings from the provided list into a natural-language
    phrase.

    Designed for use as a Jinja2 filter. This function randomly selects between
    1 and `limit` items from the list, shuffles them, and joins them into a
    phrase using the specified separator and conjunction word.

    The output mimics natural phrasing:
    - One item: returned as-is.
    - Two items: joined with the conjunction word (e.g., "apple and banana").
    - Three or more: joined with the separator, and the last item prefixed by
      the conjunction word (e.g., "apple, banana, and cherry").

    If the list is empty, an empty string is returned. If `limit` is negative,
    all items are considered.

    Example:
        {{ items | random_join_phrase(", ", "and", 3) }}
        might produce: "banana, cherry and apple"

    Args:
        items (list[str]): The list of strings to choose from.
        separator (str): The string used to separate items before the final one.
        word (str): The conjunction word used before the last item (e.g., "and",
            "or").
        limit (int, optional): Maximum number of items to include. If negative,
            no limit is applied.

    Returns:
        str: A natural-language phrase of randomly selected items, or an empty string if `items` is empty.
    """

    if not items:
        return ""

    max_items = len(items)
    if limit >= 0:
        max_items = min(limit, len(items))

    count = random.randint(1, max_items)
    selection = random.sample(items, count)
    random.shuffle(selection)

    if len(selection) == 1:
        return selection[0]
    elif len(selection) == 2:
        return f"{selection[0]} {word} {selection[1]}"
    else:
        return f"{separator.join(selection[:-1])}{separator}{word} {selection[-1]}"


def _random_set(items: list[str], count: int) -> list[str]:
    """
    The method is intended as a function in the template. It randomly selects a
    subset of items from the provided list.

    Designed for use as a Jinja2 filter. This function returns a list containing
    up to `count` randomly selected items from `items`. If `count` exceeds the
    number of available items, all items are returned in random order. If the
    input list is empty, an empty list is returned.

    Unlike `_random_join` or `_random_join_phrase`, this function returns the
    raw list of selected items for further processing or formatting.

    Example:
        {{ ["apple", "banana", "cherry"] | random_set(2) }}
        generat
        might return: ["banana", "apple"]

    Args:
        items (list[str]): The list of strings to choose from.
        count (int): The number of items to select.

    Returns:
        list[str]: A randomly selected subset of items, or an empty list if `items` is empty.
    """
    if not items:
        return []
    max_items = len(items)
    actual_count = min(count, max_items)
    return random.sample(items, actual_count)


class _Template:

    def __init__(self, datasource: str, language: str):

        self.language = language
        self.variants = []
        self.filter = []
        self.environment = Environment(loader=BaseLoader(), trim_blocks=False, lstrip_blocks=False)
        self.environment.filters["annotate"] = _annotate
        self.environment.filters["random_set"] = _random_set
        self.environment.filters["random_join"] = _random_join
        self.environment.filters["random_join_phrase"] = _random_join_phrase

        filename = f"synthetics_{language.lower()}.yaml"
        path = os.path.join(datasource, filename)
        if not os.path.isfile(path):
            raise FileNotFoundError(f"File not found: {path}")

        with open(path, encoding="utf-8") as file:
            data = yaml.safe_load(file)
        parts = data.get("templates")
        if not isinstance(parts, list):
            return

        for index, part in enumerate(parts):
            if not part["template"]:
                continue
            name = part["condition"] or f"#{str(index)}"
            condition = str(part["condition"]) or "True"
            template = self.environment.from_string(part["template"].strip())

            try:
                if re.search(r"\b(__|import|exec|open|os|sys)\b", condition):
                    raise ValueError(f"Unsafe token in condition: {condition}")
                compile(condition, "<condition>", "eval")
            except Exception as exception:
                raise SyntaxError(f"Template {name} () {type(exception).__name__} occurred: {exception}")

            patterns = {}
            labels = []
            for span in part.get("spans", []):
                label = span.get("label")
                pattern = span.get("pattern")
                if label:
                    if label not in labels:
                        labels.append(label)
                    patterns[label] = re.compile(pattern)
            spans = {label: patterns[label] for label in labels}

            try:
                template.render({})
                self.variants.append((template, condition, spans))
            except Exception as exception:
                raise SyntaxError(f"Template {name} {type(exception).__name__} occurred: {exception}")

    def generate(self, data: dict[str, Any]) -> tuple[Any, str, dict[str, Any], str]:

        context = dict(data or {})
        context["random"] = random
        context["re"] = re

        templates = []
        for template, condition, spans in self.variants:
            if condition is None or eval(condition, {"__builtins__": {}}, context):
                templates.append((template, condition, spans))
        if not templates:
            return None, "", {}, ""
        selection = [template for template in templates if template not in self.filter]
        if selection:
            template, condition, spans = random.choice(selection)
            self.filter.append((template, condition, spans))
        else:
            template, condition, spans = random.choice(templates)
        if len(self.filter) >= len(self.variants):
            self.filter.clear()

        content = (template.render(**context)).strip()
        content = re.sub(r'(\r\n)|(\n\r)|(\r)', '\n', content)
        content = re.sub(r'\\\n', '', content)

        return template, condition, spans, content


_TEMPLATES: dict[tuple[str, str], _Template] = {}


@dataclass
class SyntheticResult:
    """
    Represents the result of a synthetic text generation process,
    including both raw and annotated text, as well as entity and span metadata.

    Attributes:
        text (str): The raw generated text without annotations.
        annotation (str): The annotated version of the text, including entity
            markers.
        entities (list[tuple[int, int, str]]): A list of entities found in the
            text. Each entity is represented as a tuple (start_index, end_index,
            label).
        spans (list[tuple[int, int, str]]): A list of pattern-based spans in the
            text. Each span is represented as a tuple (start_index, end_index,
            label).
    """
    text: str
    annotation: str
    entities: list[tuple[int, int, str]]
    spans: list[tuple[int, int, str]]


def _extract_entities(text: str, patterns: dict[str, Any] = None) -> SyntheticResult:

    if patterns is None:
        patterns = []
    entities: list[tuple[int, int, str]] = []
    plaintext = ""
    last_end = 0

    # In the context of text processing, a targeted search is made for
    # constellations in which markers are combined with decimal numbers,
    # enumerations, abbreviations or initials. In such cases, there is a risk
    # that spaCy will interpret the adjacent dot as part of a token, thereby
    # shifting the token boundaries.
    #
    # To avoid this, an additional space is inserted between the entity and the
    # punctuation mark when a punctuation mark immediately follows a tag. This
    # ensures that spaCy correctly recognizes the punctuation marks as separate
    # tokens and that the entity spans can be calculated reliably.
    for pattern in _ENTITY_MARKER_SPACE_PATTERN:
        text = pattern.sub(r"\g<entity_space_prefix> \g<entity_space_suffix>", text)

    for match in _ENTITY_MARKER_PATTERN.finditer(text):
        span_start, span_end = match.span()

        label = match.group("entity_label")
        value = match.group("entity_intermediate_text")

        # Intermediate text, text without marker between the last end position
        # (cursor) and the current location of the marker being searched for.
        # The intermediate text is taken over and the cursor is repositioned at
        # the end of the plain text so that the correct span positions can be
        # calculated based on the plain text.
        intermediate_text = text[last_end:span_start]
        plaintext += intermediate_text

        try:
            entity_name = label
            entity_start = len(plaintext)
            entity_end = entity_start + len(value)
            plaintext += value
            entities.append((entity_start, entity_end, entity_name))
        except ValueError:
            plaintext += value

        last_end = span_end

    # text at the end, if no marker follows must be adopted
    plaintext += text[last_end:]

    entity_starts = {start for start, end, label in entities}
    entity_ends = {end for start, end, label in entities}

    spans: list[tuple[int, int, str]] = []
    for label, pattern in patterns.items():
        for match in pattern.finditer(plaintext):
            start, end = match.start(), match.end()
            if start in entity_starts and end in entity_ends:
                spans.append((start, end, label))

    return SyntheticResult(plaintext, text, entities, spans)


def synthetics(datasource: str, language: str, data: dict[str, Any]) -> SyntheticResult:
    """
    Generates synthetic text using predefined YAML templates.

    The function loads templates from a language-specific YAML file (e.g.
    'synthetics_en.yaml'), evaluates conditions associated with each template,
    randomly selects one of the matching entries, and renders it using Jinja2.

    Templates are cached internally to improve performance on repeated
    invocations.

    Parameters:
        datasource (str): Path to the directory containing the YAML template
            files.
        language (str or Enum): Language identifier used to select the correct
            template file.
        data (dict): Contextual data used to evaluate conditions and render the
            template.

    Returns:
        SyntheticResult: A dataclass containing the generated synthetic text,
        its annotated version, and metadata about entities and spans.

        Example:
            SyntheticResult(
                text="The Earth is a planet.",
                annotation="The [[[PLANET]]]Earth[[[-]]] is a [[[TERM]]]planet[[[-]]].",
                entities=[(4, 9, "PLANET"), (15, 21, "TERM")],
                spans = [(4, 9, "PAIR"), (15, 21, "PAIR")]
            )
    """
    if not language or not language.strip():
        return SyntheticResult("", "", [], [])
    signature = (datasource or "", language)
    if signature not in _TEMPLATES:
        _TEMPLATES[signature] = _Template(datasource=datasource, language=language)
    template = _TEMPLATES[signature]
    template, condition, spans, content = template.generate(data)
    if not template:
        return SyntheticResult("", "", [], [])
    return _extract_entities(content, spans)
