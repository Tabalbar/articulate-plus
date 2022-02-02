from .temporal_utils import TemporalUtils
from .tokenizer_utils import TokenizerUtils


class EntityPOSAndTemporalFilter:
    def __init__(self):
        pass

    @staticmethod
    def filter_on_verb_pos(tokens):
        for token in tokens:
            if not token._.is_entity:
                continue

            if token._.entity == 'winmgmt' and token.pos_ == 'VERB' and token.tag_ not in ['VBP', 'MD']:
                continue

            if token._.entity == 'winmgmt' and token.pos_ == 'ADJ' and token._.entity_value[0] in ['maximize',
                                                                                                   'minimize']:
                continue

            if token._.entity == 'winmgmt':
                TokenizerUtils.clear_entity(token)

            if token.pos_ in ['NOUN', 'PROPN']:
                continue

            TokenizerUtils.clear_entity(token)

    @staticmethod
    def filter_on_temporal_entities(tokens):
        for token in tokens:
            if TemporalUtils.is_temporal_attribute(token._.entity):
                token._.set('is_temporal', True)
            if TemporalUtils.is_discrete_temporal_attribute(token._.entity):
                token._.set('is_discrete_temporal', True)
            if TemporalUtils.is_continuous_temporal_attribute(token._.entity):
                token._.set('is_continuous_temporal', True)

    def __call__(self, doc):
        if not doc:
            return doc

        EntityPOSAndTemporalFilter.filter_on_verb_pos(doc)
        EntityPOSAndTemporalFilter.filter_on_temporal_entities(doc)

        return doc
