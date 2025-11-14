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
        """
        Optional preprocessing for sentence normalization.

        This method can be overridden by language-specific schemas to provide a
        preprocessing function that rewrites or normalizes sentences before they
        are passed to the main Stanza pipeline. Typical use cases include
        replacing everyday logical words or phrases with forms that better align
        with Universal Dependencies conventions.

        Returns:
            Callable[[Sentence], list[str]] | None:
                A function that accepts a Stanza Sentence object and returns a
                list of strings representing the preprocessed sentence(s). If no
                preprocessing is required, returns None.
        """
        return None

#   @abstractmethod
#   def find_markers(self, sentence: Sentence, word: Word) -> frozenset[str]:
        ...

    def infer_relation_root(self, sentence: Sentence, word: Word) -> int:
        """
        Infer the root entity relation for a word in the dependency tree.

        This method traverses the dependency chain upward (following head) and
        identifies the highest ancestor word that is associated with an entity.
        Unlike infer_relation_head, which stops at the first parent entity,this
        method continues to traverse the chain and returns the top-most entity
        node.

        Args:
            sentence (Sentence): The Stanza sentence containing the word.
            word (Word): The word whose root entity relation is to be inferred.

        Returns:
            int: The ID of the highest ancestor word that carries an entity.
                 Returns 0 if no entity is found in the chain (root).
        """
        root = 0
        while word.head > 0:
            word = sentence.words[word.head - 1]
            if word.entity is not None:
                root = word.id
        return root

    def infer_relation_head(self, sentence: Sentence, word: Word) -> int:
        """
        Infer the head (parent) relation for a word in the dependency tree.

        This method traverses the dependency chain upward until it finds a
        parent word that is associated with an entity. If no such parent exists,
        the root (0) is returned. This ensures that relations are anchored to
        meaningful entity nodes rather than arbitrary tokens.

        Args:
            sentence (Sentence): The Stanza sentence containing the word.
            word (Word): The word whose head relation is to be inferred.

        Returns:
            int: The ID of the parent word that carries an entity, or 0 if no
            entity parent exists (root).
        """
        while word.head > 0:
            word = sentence.words[word.head - 1]
            if word.entity is not None:
                return word.id
        return 0

    def infer_relation(self, sentence: Sentence, word: Word) -> Relation:
        """
        Infer the relation (head and cluster) for a word.

        This method provides a default implementation that assigns the word
        itself as its cluster and sets the head to root (0). Language-specific
        schemas can override this method to apply more refined rules based on
        dependency relations, part-of-speech tags, or morphological features.

        Args:
            sentence (Sentence): The Stanza sentence containing the word.
            word (Word): The word whose relation is to be inferred.

        Returns:
            Relation: A Relation object containing the inferred head, cluster,
            and any associated features.
        """
        return Relation(head=0, cluster=word.id)
