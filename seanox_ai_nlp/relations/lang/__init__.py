# seanox_ai_nlp/relations/lang/__init__.py

from .abstract import Schema
from .de import SchemaDE
from .dk import SchemaDK
from .en import SchemaEN
from .es import SchemaES
from .fr import SchemaFR
from .it import SchemaIT
from .ru import SchemaRU
from .default import SchemaDefault


_SCHEMAS: dict[str, type[Schema]] = {
    "de": SchemaDE,
    "dk": SchemaDK,
    "en": SchemaEN,
    "es": SchemaES,
    "fr": SchemaFR,
    "it": SchemaIT,
    "ru": SchemaRU
}


def languages() -> frozenset[str]:
    return frozenset(_SCHEMAS.keys())


def language_schema(lang: str) -> Schema:
    if lang not in _SCHEMAS:
        return SchemaDefault()
    return _SCHEMAS[lang]()


__all__ = [
    "Schema",
    "languages",
    "language_schema"
]
