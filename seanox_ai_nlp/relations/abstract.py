# seanox_ai_npl/relations/abstract.py

from typing import NamedTuple


class Entity(NamedTuple):
    start: int
    end: int
    label: str
    text: str
