from .corpus_entity_extractor import CorpusEntityExtractor


class ContextBasedCorpusEntityExtractor(CorpusEntityExtractor):
    def __init__(self, named_entities, regular_expressions, entity_lookup):
        super().__init__(named_entities=named_entities, regular_expressions=regular_expressions,
                         entity_lookup=entity_lookup)

    def get_subject_tokens(self, contexts, tokenize=True,
                           include_setup=True, include_request=True, include_conclusion=True):
        subject_tokens_by_context = []
        for context in contexts:
            setup_utterances = CorpusEntityExtractor.preprocess_utterances_from_annotations(
                annotations=context.get_setup())
            tokenized_setups = self.get_tokens(utterances=setup_utterances, tokenize=tokenize)
            request_utterances = CorpusEntityExtractor.preprocess_utterances_from_annotations(
                annotations=[context.get_request()])
            tokenized_requests = self.get_tokens(utterances=request_utterances, tokenize=tokenize)
            conclusion_utterances = CorpusEntityExtractor.preprocess_utterances_from_annotations(
                annotations=context.get_conclusion())
            tokenized_conclusions = self.get_tokens(utterances=conclusion_utterances, tokenize=tokenize)

            utterance_type = context.get_request().get_utterance().get_utterancetype_attribute()

            subject_tokens = (utterance_type,)
            if include_setup:
                subject_tokens += (tokenized_setups,)
            else:
                subject_tokens += (None,)
            if include_request:
                subject_tokens += (tokenized_requests,)
            else:
                subject_tokens += (None,)
            if include_conclusion:
                subject_tokens += (tokenized_conclusions,)
            else:
                subject_tokens += (None,)

            subject_tokens_by_context.append(subject_tokens)
        return subject_tokens_by_context
