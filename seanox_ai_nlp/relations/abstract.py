# seanox_ai_npl/relations/abstract.py

from typing import NamedTuple


class Entity(NamedTuple):
    start: int
    end: int
    label: str
    text: str
    semantic: bool = True

    def __eq__(self, other):
        if not isinstance(other, Entity):
            return NotImplemented
        if self.semantic and other.semantic:
            return (self.text, self.label) == (other.text, other.label)
        return tuple(self) == tuple(other)

    def __hash__(self):
        if self.semantic:
            return hash((self.text, self.label))
        return hash(tuple(self))
