# seanox_ai_npl/relations/lang/de.py

from seanox_ai_nlp.relations.lang.abstract import Relations

from stanza.models.common.doc import Word, Sentence

class RelationsDE(Relations):

    def infer_logical_relation(self, sentence: Sentence, word: Word) -> int:
        return word.head
