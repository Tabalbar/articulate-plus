import abc
import itertools
from abc import ABCMeta

from ..corpus_extractor import UtteranceProcessingUtils
from ..text_tokenizer_pipeline.text_processing_utils import TextProcessingUtils


class Segmenter(metaclass=ABCMeta):
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        # corpus utterances segmented according to annotations (by subject)
        self._segments_by_subject = {}

        # this is a dictionary (key is subject, i.e., "subject5") and value is an utterance from the corpus dialogue.
        self._utterances_by_subject = {}

    def _clean_utterance(self, utterance):
        return UtteranceProcessingUtils.clean_utterance(
            TextProcessingUtils.clean_text(
                text=utterance, lowercase=True,
                remove_punctuation=True), remove_hyphens=True)

    def get_utterances_by_subject(self):
        if self._utterances_by_subject:
            return self._utterances_by_subject

        if not self._segments_by_subject:
            return None

        for subject, utterances in self._segments_by_subject.items():
            if subject not in self._utterances_by_subject:
                self._utterances_by_subject[subject] = []

            self._utterances_by_subject[subject] += itertools.chain(*utterances)

        return self._utterances_by_subject

    @abc.abstractmethod
    def get_segments_by_subject(self, unseen_subjects, fold=0):
        pass
