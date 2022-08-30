from .corpus_entity_extractor import CorpusEntityExtractor


class RequestBasedCorpusEntityExtractor(CorpusEntityExtractor):
    def __init__(self, named_entities, regular_expressions, entity_lookup):
        super().__init__(named_entities=named_entities, regular_expressions=regular_expressions,
                         entity_lookup=entity_lookup)

    def get_subject_tokens(self, contexts, tokenize=True, \
                           include_setup=True, include_request=True, include_conclusion=True):

        subject_tokens_by_context = []
        for context in contexts:
            setup_utterances = CorpusEntityExtractor.preprocess_utterances_from_annotations(
                annotations=context.get_setup())
            request_utterances = CorpusEntityExtractor.preprocess_utterances_from_annotations(
                annotations=[context.get_request()])
            conclusion_utterances = CorpusEntityExtractor.preprocess_utterances_from_annotations(
                annotations=context.get_conclusion())
            utterance_type = context.get_request().get_utterance().get_utterancetype_attribute()

            subject_tokens = []
            if include_setup:
                subject_tokens += setup_utterances
            if include_request:
                subject_tokens += request_utterances
            if include_conclusion:
                subject_tokens += conclusion_utterances

            tokenized = self.get_tokens(subject_tokens, tokenize=tokenize)
            subject_tokens_by_context.append((utterance_type, tokenized))

        return subject_tokens_by_context
