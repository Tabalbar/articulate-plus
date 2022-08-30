from spacy.util import filter_spans


class TokenizerUtils:
    @staticmethod
    def clear_entity(token):
        token._.set('is_entity', False)
        token._.set('entity', None)
        token._.set('entity_source', None)
        token._.set('is_entity_name', False)
        token._.set('is_temporal', False)
        token._.set('is_discrete_temporal', False)
        token._.set('is_continuous_temporal', False)
        token._.set('entity_value', None)
        token._.set('entity_children', None)
        token._.set('entity_data_attribute', None)
        # token._.set('is_y_axis', None)

    @staticmethod
    def char_indices_to_token_indices(doc, start_char_idx, end_char_idx):
        curr_char_idx = 0

        tokens = [token.text for token in doc]

        for start_token_idx, token in enumerate(tokens):
            if curr_char_idx >= start_char_idx:
                break
            curr_char_idx += len(token) + 1

        if start_token_idx == len(tokens) - 1 and curr_char_idx + len(tokens[start_token_idx]) == end_char_idx:
            return start_token_idx, start_token_idx + 1

        for end_token_idx, token in enumerate(tokens[start_token_idx:]):
            curr_char_idx += len(token) + 1
            if curr_char_idx >= end_char_idx:
                break

        return start_token_idx, start_token_idx + end_token_idx + 1

    @staticmethod
    def get_non_overlapping_token_spans_from_char_spans(doc, char_spans):
        return filter_spans(
            [
                doc[token_span[0]:token_span[1]] for token_span in [
                    TokenizerUtils.char_indices_to_token_indices(
                        doc=doc,
                        start_char_idx=start,
                        end_char_idx=end
                    ) for start, end in char_spans
                ]
            ]
        )

    @staticmethod
    def merge_tokens(doc, token_spans):
        if token_spans is None:
            return

        with doc.retokenize() as retokenizer:
            for token_span in token_spans:
                retokenizer.merge(doc[token_span.start:token_span.end])
