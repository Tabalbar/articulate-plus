import re

from flashtext import KeywordProcessor
from nltk.tokenize import word_tokenize
from spacy.tokens import Doc, Token, Span

from .text_processing_utils import TextProcessingUtils
from .text_span import TextSpan
from .tokenizer import Tokenizer
from .tokenizer_utils import TokenizerUtils


class TextTokenizer(Tokenizer):
    def __init__(self, named_entities, regular_expressions, entity_lookup, vocab, is_entity_assignment=True,
                 is_entity_extraction=True):
        super().__init__()

        self.phrase_tokenizer = KeywordProcessor(case_sensitive=False)
        for named_entity in named_entities:
            entity_name = named_entity[0]
            entity_value = named_entity[1]
            self.phrase_tokenizer.add_keyword(entity_value, entity_name)

        self.regular_expressions = regular_expressions

        self.vocab = vocab

        self.entity_lookup = entity_lookup

        self.is_entity_assignment = is_entity_assignment

        self.is_entity_extraction = is_entity_extraction

        if self.is_entity_extraction:
            Token.set_extension('is_entity', default=False, force=True)
            Token.set_extension('is_entity_name', default=False, force=True)
            Token.set_extension('entity_source', default=None, force=True)
            Token.set_extension('start_char', default=-1, force=True)
            Token.set_extension('end_char', default=-1, force=True)
            Token.set_extension('entity', default=None, force=True)
            Token.set_extension('is_temporal', default=False, force=True)
            Token.set_extension('is_discrete_temporal', default=False, force=True)
            Token.set_extension('is_continuous_temporal', default=False, force=True)
            Token.set_extension('entity_children', default=None, force=True)
            Token.set_extension('entity_data_attribute', default=None, force=True)
            Token.set_extension('entity_value', default=None, force=True)
            Token.set_extension('entity_value', default=None, force=True)
            # Token.set_extension('is_y_axis', default=None, force=True)

            Doc.set_extension('entities', getter=self.get_entities, force=True)
            Span.set_extension('entities', getter=self.get_entities, force=True)

    def get_entities(self, tokens):
        return [token for token in tokens if token._.is_entity == True]

    def span_tokenize_on_regexp(self, text, regexp):
        processed_text = text.lower()
        target_spans = []
        for match in re.finditer(regexp, processed_text):
            start = match.span()[0]
            end = match.span()[1]
            target_spans.append(TextSpan(span=range(start, end), matching_token=regexp))
        return target_spans

    def span_tokenize_on_phrases(self, text):
        processed_text = text.lower()
        processed_text = TextProcessingUtils.lemmatize_text(processed_text)

        target_spans = []
        end = 0
        for entity_name, matching_phrase_start_char, matching_phrase_end_char \
                in self.phrase_tokenizer.extract_keywords(processed_text, span_info=True):

            start_token_span = len(word_tokenize(processed_text[:matching_phrase_start_char]))
            end_token_span = start_token_span + len(word_tokenize(
                processed_text[matching_phrase_start_char:matching_phrase_end_char]))

            matching_phrase_in_text = ' '.join(word_tokenize(text)[\
                                               start_token_span:end_token_span])

            if len(matching_phrase_in_text.strip()) == 0:
                continue

            start = text[end:].find(matching_phrase_in_text)
            start += len(text[:end])
            end = start + len(matching_phrase_in_text)

            matching_token = processed_text[matching_phrase_start_char:matching_phrase_end_char]
            target_spans.append(TextSpan(span=range(start, end), matching_token=matching_token))

        return target_spans

    def span_tokenize_on_hyphens(self, text):
        target_spans = self.span_tokenize_on_regexp(text, "\\b[a-zA-Z0-9?.*]*-[^\\s]+\\b")
        return target_spans

    def __call__(self, text, apply_hyphen_tokenization=True,
                 apply_regular_expression_tokenization=True, apply_phrase_tokenization=True):
        word_tokenized = word_tokenize(text)
        processed_text = ' '.join(word_tokenized)
        spans = []

        if apply_hyphen_tokenization:
            hyphen_spans = self.span_tokenize_on_hyphens(processed_text)
            spans += hyphen_spans

        if apply_regular_expression_tokenization:
            for regular_expression in self.regular_expressions:
                regular_expression_spans = self.span_tokenize_on_regexp(
                    processed_text, regular_expression)
                spans += regular_expression_spans

        if apply_phrase_tokenization:
            phrase_spans = self.span_tokenize_on_phrases(processed_text)
            spans += phrase_spans

        spaces = [True] * len(word_tokenized)
        doc = Doc(self.vocab, words=word_tokenized, spaces=spaces)

        if len(spans) == 0:
            return doc

        try:
            TokenizerUtils.merge_tokens(
                doc=doc,
                token_spans=TokenizerUtils.get_non_overlapping_token_spans_from_char_spans(
                    doc=doc,
                    char_spans=[(span.get_start(), span.get_end()) for span in spans])
            )
        except Exception as e:
            print("Error merging text", doc.text)
            raise e

        if self.is_entity_extraction:
            tokens = {(span.get_start(), span.get_end()): span.get_matching_token() \
                      for span in spans}

            end = 0
            for token in doc:
                start = processed_text[end:].find(token.text)
                start += len(processed_text[:end])
                end = start + len(token)

                token._.set('start_char', start)
                token._.set('end_char', end)

                match = None
                if (start, end) in tokens:
                    match = tokens[(start, end)]
                    token._.set('is_entity', True)

                token._.set('entity_source', match)

                if self.is_entity_assignment:
                    token_entity_source = token._.entity_source
                    if not token_entity_source:
                        token_entity_source = self.entity_lookup.get_closest_term(token.text)

                    if token_entity_source:
                        token._.set('is_entity', True)

                    lookup_entity_name = self.entity_lookup.get_name(token_entity_source)
                    token._.set('entity', lookup_entity_name)

                    token._.set('entity_value', None)
                    matched_values = self.entity_lookup.get_matched_values(token_entity_source)

                    token._.set('entity_value', matched_values)

                    token._.set('entity_data_attribute', None)
                    matched_data_attributes = self.entity_lookup.get_matched_data_attributes(token_entity_source)
                    token._.set('entity_data_attribute', matched_data_attributes)

                    token._.set('is_entity_name', self.entity_lookup.get_is_named_entity_category(token_entity_source))
                    token._.set('entity_children', None)
                    if self.entity_lookup.get_is_named_entity_category(token_entity_source):
                        token._.set('entity_children',
                                    list(self.entity_lookup.get_entity_values(lookup_entity_name).keys()))

        return doc
