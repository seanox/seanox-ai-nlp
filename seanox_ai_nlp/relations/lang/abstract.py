# seanox_ai_npl/relations/abstract.py

from abc import ABC, abstractmethod
from enum import Enum, auto
from stanza.models.common.doc import Sentence, Word
from typing import Callable, NamedTuple, FrozenSet


class Feature(Enum):
    NEGATION = auto()
    CONTRAST = auto()


class Relation(NamedTuple):
    head: int
    cluster: int
    features: FrozenSet[Feature] = frozenset()


# TODO: Check RELATIVE and CLAUSE for deprel / upos relevance
#       PrimitiveMarker should only contain deprel-/upos-relevant constants.
class PrimitiveMarker(Enum):
    NMOD = "nmod"
    PREP = "prep"
    RELATIVE = "relative"
    CLAUSE = "clause"
    CC = "cc"
    CONJ = "conj"
    ADP = "adp"


class SyntacticMarkers(Enum):
    COORDINATION = "coordination"


class MorphologicalMarkers(Enum):
    NEGATION = "negation"
    COMPARATIVE = "comparative"
    SUPERLATIVE = "superlative"


class ConnectorMarkers(Enum):
    ADVERSATIVE = "adversative"
    CAUSAL = "causal"
    CONCESSIVE = "concessive"
    FINAL = "final"


class Schema(ABC):

    def sentence_preprocessor(self) -> Callable[[Sentence], list[str]] | None:
        return None

#   @abstractmethod
#   def find_markers(self, sentence: Sentence, word: Word) -> frozenset[str]:
        ...

    def infer_relation_head(self, sentence: Sentence, word: Word) -> int:
        while word.head > 0:
            parent = sentence.words[word.head - 1]
            if getattr(parent, "entity", None) is not None:
                return parent.id
            word = parent
        return 0

    def infer_relation(self, sentence: Sentence, word: Word) -> Relation:
        return Relation(head=0, cluster=word.id)

