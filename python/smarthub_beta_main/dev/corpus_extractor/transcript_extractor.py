import glob
from collections import defaultdict

from .utterance_processing_utils import UtteranceProcessingUtils
from ..corpus_feature_extractor.corpus_feature_extractor_utils import CorpusFeatureExtractorUtils
from ..text_tokenizer_pipeline.text_processing_utils import TextProcessingUtils


class TranscriptExtractor:
    @staticmethod
    def get_transcripts(path):
        entityextractor = CorpusFeatureExtractorUtils. \
            get_context_based_corpus_entity_extractor()
        utterances_by_subject = defaultdict(list)
        for file_path in glob.glob(path + '*.txt'):
            subject_name = file_path[len(path):-len('.txt')]
            utterances = []
            with open(file_path, 'r') as f:
                for text in f:
                    cleaned_text = TranscriptExtractor.preprocess_utterance(text)
                    if 'experimentor' in cleaned_text:
                        continue
                    if cleaned_text == 'start':
                        continue
                    if cleaned_text == 'end':
                        continue
                    utterances.append(cleaned_text)

            utterances_by_subject[subject_name] += [entityextractor.entity_nlp(utterance) for utterance in utterances]
        return utterances_by_subject

    @staticmethod
    def preprocess_utterance(text):
        return UtteranceProcessingUtils.clean_utterance(
            TextProcessingUtils.clean_text(
                text=text, lowercase=True,
                remove_punctuation=True), remove_hyphens=True)
