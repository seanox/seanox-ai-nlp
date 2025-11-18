# seanox_ai_npl/relations/abstract.py

from abc import ABC
from enum import Enum
from stanza.models.common.doc import Sentence, Word
from typing import Callable

from seanox_ai_nlp.relations.abstract import Entity


class UPOS(Enum):
    ADJ = "ADJ"
    ADP = "ADP"
    ADV = "ADV"
    AUX = "AUX"
    CCONJ = "CCONJ"
    DET = "DET"
    INTJ = "INTJ"
    NOUN = "NOUN"
    NUM = "NUM"
    PART = "PART"
    PRON = "PRON"
    PROPN = "PROPN"
    PUNCT = "PUNCT"
    SCONJ = "SCONJ"
    SYM = "SYM"
    VERB = "VERB"
    X = "X"


class DEPREL(Enum):
    ROOT = "root"
    NSUBJ = "nsubj"
    OBJ = "obj"
    IOBJ = "iobj"
    OBL = "obl"
    NMOD = "nmod"
    AMOD = "amod"
    ADVMOD = "advmod"
    DET = "det"
    CASE = "case"
    CC = "cc"
    CONJ = "conj"
    PUNCT = "punct"
    COMPOUND = "compound"
    APPOS = "appos"
    VOCATIVE = "vocative"
    MARK = "mark"
    AUX = "aux"
    COP = "cop"
    DISCOURSE = "discourse"


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

    def infer_word_path(self, sentence: Sentence, word: Word) -> tuple[int, ...]:
        """
        Infer the dependency path of a word within a sentence.

        This method provides the sequence of parent nodes that connect a word
        back to the root of the sentence. The path can be used by applications
        to understand how a word is positioned in the grammatical structure,
        which is helpful for tasks such as clustering, relation extraction, or
        linking words to higher‑level entities.

        Args:
            sentence (Sentence): The sentence object containing the word.
            word (Word): The word whose dependency path should be retrieved.

        Returns:
            tuple[int, ...]: A sequence of IDs representing the word’s path
            from the root of the sentence down to the word itself.
        """
        path: list[int] = []
        while True:
            path.append(word.head)
            if word.head <= 0:
                break
            word = sentence.words[word.head - 1]
        path.reverse()
        return tuple(path)

    def annotate_words(self, sentence: Sentence, entities: list[Entity]) -> None:

        if not sentence or not sentence.words:
            return

        # In the default implementation, the sentence  root is used as the base
        # cluster. The idea is that annotate_words is rarely overwritten and the
        # logical cluster assignment is performed with refinement_words.
        cluster = self.infer_word_path(sentence, sentence.words[0])[:2]

        # Annotate words, path, default cluster, and entity are set.
        # Ignore MWT (Multi-Word Token without start_char).
        for word in sentence.words:
            word.path = self.infer_word_path(sentence, word)
            word.cluster = cluster
            if word.start_char is not None:
                for entity in entities:
                    if entity.start <= word.start_char < entity.end:
                        word.entity = entity
                        break

    def refinement_words(self, sentence: Sentence, entities: list[Entity]) -> None:
        pass
