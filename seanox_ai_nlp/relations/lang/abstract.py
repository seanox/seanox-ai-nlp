# seanox_ai_npl/relations/abstract.py

from abc import ABC, abstractmethod

from stanza.models.common.doc import Sentence, Word


class Relations(ABC):

    @abstractmethod
    def find_markers(self, sentence: Sentence, word: Word) -> frozenset[str]:
        ...

    @abstractmethod
    def find_logical_relation(self, sentence: Sentence, word: Word) -> int:
        ...
