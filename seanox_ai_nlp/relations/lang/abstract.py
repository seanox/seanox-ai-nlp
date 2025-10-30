# seanox_ai_npl/relations/abstract.py

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
from typing import Callable
from stanza.models.common.doc import Sentence, Word

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


class Relations(ABC):

    def sentence_preprocessor(self) -> Callable[[Sentence], list[str]] | None:
        return None

#   @abstractmethod
#   def find_markers(self, sentence: Sentence, word: Word) -> frozenset[str]:
        ...

    def infer_relations(self, sentence: Sentence, word: Word) -> Relations:
        from seanox_ai_nlp.relations.relations import Relations
        return Relations(head=0, associations=[word.id])
