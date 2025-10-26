# seanox_ai_npl/relations/abstract.py

from abc import ABC, abstractmethod
from typing import Callable

from stanza.models.common.doc import Sentence, Word


class Relations(ABC):

    def sentence_preprocessor(self) -> Callable[[Sentence], list[str]] | None:
        return None

    @abstractmethod
    def find_markers(self, sentence: Sentence, word: Word) -> frozenset[str]:
        ...

    @abstractmethod
    def find_logical_relation(self, sentence: Sentence, word: Word) -> int:
        ...
