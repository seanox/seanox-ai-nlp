# seanox_ai_npl/synthetics/synthetics.py

from jinja2 import Environment, BaseLoader, Template
from typing import Any, NamedTuple

import os
import random
import re
import yaml


def _re_compile(expression: str, debug: bool = False) -> re.Pattern:
    expression = re.sub(r"\s{2,}|[\r\n]+", "", expression)
    if not debug:
        return re.compile(expression)
    return expression


_ENTITY_MARKER_SIGNATURE_START = "|--"
_ENTITY_MARKER_SIGNATURE_END = "--|"

_ENTITY_MARKER_NAME_RAW_PATTERN = r"\w([\w\-]*\w)?"
_ENTITY_MARKER_START_RAW_PATTERN = rf"""
    (?:
        {re.escape(_ENTITY_MARKER_SIGNATURE_START)}
        (?:{_ENTITY_MARKER_NAME_RAW_PATTERN})
        {re.escape(_ENTITY_MARKER_SIGNATURE_END)}
    )
"""
_ENTITY_MARKER_END_RAW_PATTERN = rf"""
    (?:
        {re.escape(_ENTITY_MARKER_SIGNATURE_START)}
        -
        {re.escape(_ENTITY_MARKER_SIGNATURE_END)}
    )
"""
_ENTITY_MARKER_RAW_PATTERN = rf"""
    ({_ENTITY_MARKER_START_RAW_PATTERN})
    (.*?)
    ({_ENTITY_MARKER_END_RAW_PATTERN})
"""

_ENTITY_MARKER_NAME_PATTERN = re.compile(_ENTITY_MARKER_NAME_RAW_PATTERN)
_ENTITY_MARKER_PATTERN = re.compile(_ENTITY_MARKER_RAW_PATTERN)
_ENTITY_MARKER_ANTI_PATTERN = [
    re.compile(rf"{_ENTITY_MARKER_RAW_PATTERN}([\.\,\:/]){_ENTITY_MARKER_RAW_PATTERN}"),
    re.compile(rf"(\w)([\.\,\:/]){_ENTITY_MARKER_RAW_PATTERN}"),
    re.compile(rf"{_ENTITY_MARKER_RAW_PATTERN}([\.\,\:/])(\w)"),
]
_ENTITY_MARKER_SPACE_PATTERN = [
    re.compile(rf"({_ENTITY_MARKER_START_RAW_PATTERN}.*?{_ENTITY_MARKER_END_RAW_PATTERN})([\.\,\:/])"),
    re.compile(rf"([\)\]\s]/)({_ENTITY_MARKER_START_RAW_PATTERN})"),
    re.compile(rf"({_ENTITY_MARKER_END_RAW_PATTERN})([\)\]\"\'])"),
]


def _annotate(data):
    if not isinstance(data, tuple) or len(data) < 2:
        return data
    key, value = data
    if not isinstance(key, str) or not _ENTITY_MARKER_NAME_PATTERN.match(key):
        return data
    return f"{_ENTITY_MARKER_SIGNATURE_START}{key}|{value}{_ENTITY_MARKER_SIGNATURE_END}"


class _Template:

    def __init__(self, datasource: str, language: str):

        self.language = language
        self.variants = []
        self.filter = []
        self.environment = Environment(loader=BaseLoader(), trim_blocks=False, lstrip_blocks=False)
        self.environment.filters["annotate"] = _annotate

        filename = f"synthetics_{language.lower()}.yaml"
        path = os.path.join(datasource, filename)
        if not os.path.isfile(path):
            raise FileNotFoundError(f"File not found: {path}")

        print(path)
        with open(path, encoding="utf-8") as file:
            parts = yaml.safe_load(file)

        if not isinstance(parts, list):
            return

        for index, part in enumerate(parts):
            if not part["template"]:
                continue
            name = part["condition"] or  f"#{str(index)}"
            condition = str(part["condition"]) or "True"
            template = self.environment.from_string(part["template"].strip())

            try:
                if re.search(r"\b(__|import|exec|open|os|sys)\b", condition):
                    raise ValueError(f"Unsafe token in condition: {condition}")
                compile(condition, "<condition>", "eval")
            except Exception as exception:
                raise SyntaxError(f"Template {name} () {type(exception).__name__} occurred: {exception}")

            try:
                template.render(
                    {},
                    random_join=lambda separator, items, *args: separator.join(items),
                    random_set=lambda items, count: items[:count] if count <= len(items) else items,
                    random_join_phrase = lambda separator, word, items, *args: separator.join(items)
                )
                self.variants.append((template, condition))
            except Exception as exception:
                raise SyntaxError(f"Template {name} {type(exception).__name__} occurred: {exception}")

    def generate(self, data: dict[str, Any]) -> str:

        context = dict(data or {})
        context["random"] = random
        context["re"] = re

        templates = []
        for template, condition in self.variants:
            if condition is None or eval(condition, {"__builtins__": {}}, context):
                templates.append(template)
        if not templates:
            return ""
        selection = [template for template in templates if template not in self.filter]
        if selection:
            template = random.choice(selection)
            self.filter.append(template)
        else:
            template = random.choice(templates)
        if (len(self.filter) >= len(self.variants)):
            self.filter.clear()

        def random_join(separator: str, items: list[str], limit: int = -1) -> str:
            if not items:
                return ""
            max_items = len(items)
            if limit >= 0:
                max_items = min(limit, len(items))
            count = random.randint(1, max_items)
            selection = random.sample(items, count)
            random.shuffle(selection)
            return separator.join(selection)

        def random_join_phrase(separator: str, word: str, items: list[str], limit: int = -1) -> str:

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

        def random_set(items: list[str], count: int) -> list[str]:
            if not items:
                return []
            max_items = len(items)
            actual_count = min(count, max_items)
            return random.sample(items, actual_count)

        content = (template.render(
            **context,
            random_join=random_join,
            random_set=random_set,
            random_join_phrase=random_join_phrase
        )).strip()
        content = re.sub(r'(\r\n)|(\n\r)|(\r)', '\n', content)
        content = re.sub(r'\\\n', '', content)
        return content

_TEMPLATES: dict[tuple[str, str], _Template] = {}


class SyntheticResult(NamedTuple):
    text: str
    annotation: str
    entities: dict[str, Any]


def _extract_entities(text: str) -> SyntheticResult:
    pass


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
        Returns a tuple containing the text and a dictionary with entity
        annotations in spaCy-compatible format.
        Example: ("The Earth is a planet.", {"entities": [(4, 9, "PLANET")]})
    """
    if not language:
        return "", {"entities": []}
    signature = (datasource or "", language)
    if signature not in _TEMPLATES:
        _TEMPLATES[signature] = _Template(datasource=datasource, language=language)
    template = _TEMPLATES[signature]
    text = template.generate(data)
    return _extract_entities(text)
