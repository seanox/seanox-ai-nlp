# seanox_ai_nlp/relations/lang/__init__.py

from .abstract import Relations
from .de import RelationsDE
from .dk import RelationsDK
from .en import RelationsEN
from .es import RelationsES
from .fr import RelationsFR
from .it import RelationsIT
from .ru import RelationsRU


_RELATIONS: dict[str, type[Relations]] = {
    "de": RelationsDE,
    "dk": RelationsDK,
    "en": RelationsEN,
    "es": RelationsES,
    "fr": RelationsFR,
    "it": RelationsIT,
    "ru": RelationsRU
}


def languages() -> frozenset[str]:
    return frozenset(_RELATIONS.keys())


def language_module(lang: str) -> Relations:
    if lang not in _RELATIONS.keys():
        raise ValueError(f"Unsupported language: {lang}")
    return _RELATIONS[lang]()


__all__ = [
    "Relations",
    "languages",
    "language_module"
]
