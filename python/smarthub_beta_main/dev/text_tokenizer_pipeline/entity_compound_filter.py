from .tokenizer_utils import TokenizerUtils


class EntityCompoundFilter:
    def __init__(self):
        pass

    @staticmethod
    def update_entity_info(start_token, start, end_token, end):
        start_token._.set('start_char', start)
        start_token._.set('end_char', end)

        if start_token._.is_entity:
            return

        if end_token._.is_entity:
            start_token._.set('entity', end_token._.entity)
            start_token._.set('is_entity', end_token._.is_entity)
            start_token._.set('is_entity_name', end_token._.is_entity_name)
            start_token._.set('entity_source', end_token._.entity_source)
            start_token._.set('is_temporal', end_token._.is_temporal)
            start_token._.set('is_discrete_temporal', end_token._.is_discrete_temporal)
            start_token._.set('is_continuous_temporal', end_token._.is_continuous_temporal)
            start_token._.set('entity_value', end_token._.entity_value)
            start_token._.set('entity_children', end_token._.entity_children)
            start_token._.set('entity_data_attribute', end_token._.entity_data_attribute)

    @staticmethod
    def filter_on_compound_nouns(doc):
        target_spans = []
        for token in doc:
            if token.dep_ == 'compound':
                target_spans.append((token, token._.start_char, token.head, token.head._.end_char))

        for start_token, start, end_token, end in target_spans:
            if start_token.lemma_ == 'total' and end_token._.is_entity:
                TokenizerUtils.clear_entity(end_token)

            elif end_token.lemma_ == 'total' and start_token._.is_entity:
                TokenizerUtils.clear_entity(start_token)

            EntityCompoundFilter.update_entity_info(start_token, start, end_token, end)

        try:
            TokenizerUtils.merge_tokens(
                doc=doc,
                token_spans=TokenizerUtils.get_non_overlapping_token_spans_from_char_spans(
                    doc=doc,
                    char_spans=[(start, end) for _, start, _, end in target_spans]
                )
            )
        except Exception as e:
            print("Error merging text", doc.text)
            raise e

    def __call__(self, doc):
        if not doc:
            return doc

        EntityCompoundFilter.filter_on_compound_nouns(doc=doc)

        return doc
