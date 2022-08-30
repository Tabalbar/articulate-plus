from collections import OrderedDict

from nltk.corpus import wordnet as wn
from spacy.tokens import Doc, Span

from .dependencyparser import DependencyParser
from .subject_verb_object_extract import findSVOs
from .tokenizer_utils import TokenizerUtils
from .temporal_utils import TemporalUtils


class EntityDependencyFilter:
    def __init__(self):
        Doc.set_extension('svos', getter=EntityDependencyFilter.apply_subject_verb_object, force=True)
        Span.set_extension('svos', getter=EntityDependencyFilter.apply_subject_verb_object, force=True)

    @staticmethod
    def get_temporal_prepositional_complements_indices(tokens):
        prep_complement_indices = [index for index, token in enumerate(tokens) if \
                                   token.dep_ == 'pobj' and token._.is_entity and \
                                   TemporalUtils.is_temporal_attribute(token._.entity)]

        return prep_complement_indices

    @staticmethod
    def filter_non_mergible_phrase_indices(prep_complement_indices):
        compatible = []
        incompatible = []

        for i in range(len(prep_complement_indices)):
            prep_complement_token_1 = prep_complement_indices[i]

            # the start and end span for prep complement 1
            prep_complement_token_1_span = \
                (prep_complement_token_1[1]._.start_char, prep_complement_token_1[1]._.end_char)

            for j in range(i + 1, len(prep_complement_indices)):
                prep_complement_token_2 = prep_complement_indices[j]

                # the start and end span for prep complement 2
                prep_complement_token_2_span = \
                    (prep_complement_token_2[1]._.start_char, prep_complement_token_2[1]._.end_char)

                '''if the spans are the same, then that is incompatible. That is, we don't want their phrases to be merged.
                otherwise if the spans are not the same and the tokens do not come from same phrase, then as long as
                the tokens are not in the incompatible list, we can add them to the compatible list.
                '''
                if prep_complement_token_1_span == prep_complement_token_2_span:
                    prep_complement_phrase_span = (prep_complement_token_1[0], prep_complement_token_2[0])

                    # Add to the incompatible list and remove from the compatible list if it currently exists there.
                    incompatible.append(prep_complement_phrase_span)
                    if prep_complement_phrase_span in compatible:
                        compatible.remove(prep_complement_phrase_span)
                elif prep_complement_token_1[0] != prep_complement_token_2[0]:
                    prep_complement_phrase_span = (prep_complement_token_1[0], prep_complement_token_2[0])
                    if prep_complement_phrase_span in incompatible:
                        continue
                    compatible.append(prep_complement_phrase_span)
        '''
        Return the list of compatible merges. Each item in the compatible list is a pair of phrase indices, indicating
        that those two indices are compatible for merging.
        '''
        return compatible

    @staticmethod
    def is_token_in_phrase(token, phrase):
        return (token._.start_char, token._.end_char) in \
               [(token[0]._.start_char, token[0]._.end_char) for token in phrase]

    @staticmethod
    def merge_prepositional_phrases(prepositional_phrases, token_1, token2):
        '''
        Merge each pair of phrases together that contain either or both token 1 and token 2
        '''

        '''
        Add all phrase indices that contain either token 1 or token 2 (or both)
        '''
        phrase_indices = []
        for index, phrase in enumerate(prepositional_phrases):
            for token in (token_1, token2):
                if EntityDependencyFilter.is_token_in_phrase(token, phrase):
                    phrase_indices.append((index, token))

        '''
        Certain phrases cannot be merged, so filter those out from the phrase indices list
        The original phrase indices variable is the list of pairs: (index of the phrase that token belongs to, the token itself)
        After filter-Non_mergible_phrase_indices call, the phase_indices variable is still a list of pairs, although in now,
        its just a pair of integers (phrase index 1 corresponding to phrase 1, phrase index 2 corresponding to phrase 2),
        indicating that phrases 1 and 2 are compabile for merging.
        '''
        phrase_indices = EntityDependencyFilter.filter_non_mergible_phrase_indices(phrase_indices)

        merged_prepositional_phrases = prepositional_phrases.copy()

        for phrase_index in phrase_indices:
            merged_phrase = []

            start, end = phrase_index

            '''
            Concatenate the two phrases together
            '''
            merged_phrase = prepositional_phrases[start] + prepositional_phrases[end]

            '''
            Replace the concatenated phrase from the list with the merged phrase.
            '''
            if prepositional_phrases[start] in merged_prepositional_phrases:
                merged_prepositional_phrases.remove(prepositional_phrases[start])

            if len(merged_phrase) > 0:
                merged_prepositional_phrases.append(merged_phrase)

        return merged_prepositional_phrases

    @staticmethod
    def extract_corrected_prepositional_phrases(prepositional_phrases, tokens):
        corrected_prepositional_phrases = prepositional_phrases.copy()

        '''
        Get index position for every word in current utterance that is a prepositional complement
        (pobj) and is associated with a temporal entity slot name
        '''
        prep_complement_indices = EntityDependencyFilter. \
            get_temporal_prepositional_complements_indices(tokens)

        '''
        If there are less than two such indices, then do nothing more
        '''
        if len(prep_complement_indices) < 2:
            return corrected_prepositional_phrases

        '''
        Now merge any words between each pair of prepositional complements as long as there is no conjunction.
        So for "...by months of the year", we merge "months","of","the","year" into one token, since there are no
        conjunctions (CCONJ). If the phrase had "months and year", then you would not merge all words from
        "months" through "year", since there is a conjunction in between the prepositional complements.
        '''
        for index in range(len(prep_complement_indices)):
            if index + 1 >= len(prep_complement_indices):
                break

            start = prep_complement_indices[index]
            end = prep_complement_indices[index + 1]

            if [token.dep_ for token in tokens[start:end]].count('CCONJ') > 0:
                continue

            prep_complement_token_1 = tokens[start]
            prep_complement_token_2 = tokens[end]

            # merge all prepositional phrases that contain both token 1 and token 2
            corrected_prepositional_phrases = EntityDependencyFilter.merge_prepositional_phrases(
                corrected_prepositional_phrases, prep_complement_token_1, prep_complement_token_2)
        return corrected_prepositional_phrases

    @staticmethod
    def extract_relevant_prepositional_phrases(prepositional_phrases):
        relevant_prepositional_phrases = []

        '''
        As long as you have at least 2 temporal entity slots in a given phrase, add that to the list of relevant phrases.
        '''
        for phrase in prepositional_phrases:
            if EntityDependencyFilter.get_total_number_of_temporal_entities(phrase) > 1:
                relevant_prepositional_phrases.append(phrase)

        '''
        If a relevant phrase is actually also found in a larger relevant phrase, just keep the smaller relevant phrase while
        removing the larger one. This gives us the lowest phrase in the tree.
        '''
        relevant_prepositional_phrases_cpy = relevant_prepositional_phrases.copy()
        for i in range(len(relevant_prepositional_phrases_cpy)):
            phrase_1 = ' '.join([token[1] for token in relevant_prepositional_phrases_cpy[i]])
            for j in range(i + 1, len(relevant_prepositional_phrases_cpy)):
                phrase_2 = ' '.join([token[1] for token in relevant_prepositional_phrases_cpy[j]])

                if phrase_1 in phrase_2:
                    if EntityDependencyFilter.get_total_number_of_temporal_entities(
                            relevant_prepositional_phrases_cpy[i]) > 1:
                        if relevant_prepositional_phrases_cpy[j] in \
                                relevant_prepositional_phrases:
                            relevant_prepositional_phrases.remove(
                                relevant_prepositional_phrases_cpy[j])
                    else:
                        if relevant_prepositional_phrases_cpy[i] in \
                                relevant_prepositional_phrases:
                            relevant_prepositional_phrases.remove(
                                relevant_prepositional_phrases_cpy[i])
                elif phrase_2 in phrase_1:
                    if EntityDependencyFilter.get_total_number_of_temporal_entities(
                            relevant_prepositional_phrases_cpy[j]) > 1:
                        if relevant_prepositional_phrases_cpy[i] in \
                                relevant_prepositional_phrases:
                            relevant_prepositional_phrases.remove(
                                relevant_prepositional_phrases_cpy[i])
                    else:
                        if relevant_prepositional_phrases_cpy[j] in \
                                relevant_prepositional_phrases:
                            relevant_prepositional_phrases.remove(
                                relevant_prepositional_phrases_cpy[j])
        return relevant_prepositional_phrases

    @staticmethod
    def get_total_number_of_temporal_entities(phrase):
        return len([token for token in phrase if token[0]._.is_entity and \
                    TemporalUtils.is_temporal_attribute(token[0]._.entity)])

    @staticmethod
    def filter_on_multiple_temporal_prepositional_complements(prepositional_phrases, tokens):
        '''
        For each phrase, merge appropriate tokens together. For example ("Show me crimes in river north by months of the year" would
        ask us to merge "months of the year" as one token in the prepositional phrase ("by months of the year"))
        '''
        corrected_prepositional_phrases = EntityDependencyFilter.extract_corrected_prepositional_phrases(
            prepositional_phrases, tokens)

        '''
        The corrected prepositional phrases are then fed to the relevant prepositional phrases processing to get all
        (smallest, that is  lowest on tree) prepositional phrases for which you have two temporal entity slots.
        '''
        relevant_prepositional_phrases = EntityDependencyFilter.extract_relevant_prepositional_phrases(
            corrected_prepositional_phrases)

        # If you don't have any relevant prepositional phrases, then nothing left to do
        if relevant_prepositional_phrases is None:
            return

        for phrase in relevant_prepositional_phrases:
            prep_complements = OrderedDict()

            '''
            Look for position of preposition (ADP) in phrase. Once found, search for a noun prepositional complement
            (NOUN && pobj). This will give us a ordered dictionary of (preposition word, preposition word POS, noun word, and noun POS)
            '''
            for i in range(0, len(phrase)):
                if phrase[i][3] != 'ADP':
                    continue

                prep_token = phrase[i][0]
                prep_pos = 'ADP'

                for j in range(i + 1, len(phrase)):
                    if phrase[j][3] == 'NOUN' and phrase[j][5] == 'pobj' and \
                            phrase[j][0]._.is_entity and \
                            TemporalUtils.is_temporal_attribute(phrase[j][0]._.entity):
                        noun_token = phrase[j][0]
                        noun_pos = 'NOUN'

                        prep_complements[prep_token.text] = \
                            (prep_token, prep_pos, noun_token, noun_pos)
                        break
            # If there is no ambiguity (that is, only a single noun prepositional complement or less,
            # then move on to next phrase)
            if len(prep_complements.keys()) < 2:
                continue

            '''Otherwise, we have a case of ambiguity. In that case, if any of the prepositions in the phrase are "by", then
            check what other prepositions there are (e.g. by months of the year contains "of" as the other preposition). Now,
            get the noun prepositional complement (e.g. "year") and clear its entity slot name.
            '''
            if 'by' in prep_complements:
                non_by_prep = None
                for prep in prep_complements.keys():
                    if prep != 'by':
                        non_by_prep = prep
                        break
                filter_token = prep_complements[non_by_prep][2]
                TokenizerUtils.clear_entity(filter_token)
            else:
                '''Get the second preposition (e.g. Can I get the results with months of the year". In this case,
                we have "with months of the year" phrase, and the second preposition is "of". Now get the prepositional
                complement for that preposition. In this example, that is year. Finally clear the entity slot name corresponding
                to year.
                '''
                prep_complement = list(prep_complements.keys())[1]
                filter_token = prep_complements[prep_complement][2]
                TokenizerUtils.clear_entity(filter_token)

        '''
        Finally, merge within each smallest relevant prepositional phrase, from the first occurrence of noun prepositional
        complement to the end of that utterance (e.g. "months of the year" should be merged together)
        '''
        target_spans = EntityDependencyFilter.get_all_temporal_entity_spans_from_prepositional_phrases(
            tokens,
            relevant_prepositional_phrases)
        for start_token, start, end_token, end in target_spans:
            EntityDependencyFilter.update_entity_info(start_token, start, end_token, end)

        try:
            TokenizerUtils.merge_tokens(
                doc=tokens,
                token_spans=TokenizerUtils.get_non_overlapping_token_spans_from_char_spans(
                    doc=tokens,
                    char_spans=[(start, end) for _, start, _, end in target_spans]
                )
            )
        except Exception as e:
            print("Error merging text", tokens.text)
            raise e

    @staticmethod
    def get_phrases(parsed_dependencies, pos):
        phrases = []
        for parsed_dependency in parsed_dependencies:
            for phrase in parsed_dependency.get_phrases(pos):
                phrases.append(phrase)
        return phrases

    @staticmethod
    def get_all_temporal_entity_spans_from_prepositional_phrases(doc, prepositional_phrases):
        '''
        Get the list of phrases that start at a noun prepositional complement until the end of that utterance.
        Note that this is the first occurrence of the noun prepositional complement. There can be additional
        prepositional complements between the first one until the end of the utterance.
        '''
        for phrase in prepositional_phrases:
            tokens = [token[0] for token in phrase]
            tokens = sorted(tokens, key=lambda x: (x._.start_char, x._.end_char))

            '''
            Keep looping until a noun is reached, since that is a noun prepositional complement
            '''
            index = 0
            while index < len(tokens) and tokens[index].pos_ != 'NOUN':
                index += 1

            '''
            If we reach the end of the utterance, that means there were no nouns found! So just move on to the next phrase
            '''
            if index == len(tokens):
                continue

            start = tokens[index]._.start_char
            end = tokens[-1]._.end_char

            if doc.char_span(start, end) and len(doc.char_span(start, end).text.split()) > 10:
                continue

            yield tokens[index], tokens[index]._.start_char, tokens[-1], tokens[-1]._.end_char

    @staticmethod
    def filter_on_entities_modified_by_total_adjective(adj_phrases):

        '''
        From the list of adjective phrases, if the adjective is the word "total" (or synonym of "total") and the
        adjective phrase head is a entity slot, then clear that entity slot. This addresses situations such as
        "can I see the total crimes in river north by months", in which "crimes" should no longer ne a entity slot,
        since we are not asking for crime types in this question.
        '''
        synonyms_for_total = set(['total', 'number'])
        for lemmas in [synset.lemmas() for synset in wn.synsets('total', pos=wn.NOUN)]:
            for lemma in lemmas:
                synonyms_for_total.add(lemma.name())

        for phrase in adj_phrases:
            tokens = [token[0] for token in phrase]

            index = 0
            while index < len(tokens) and tokens[index].pos_ != 'ADJ':
                index += 1

            if index == len(tokens):
                continue

            # if tokens[index].text == 'total' and \
            if tokens[index].text in synonyms_for_total and \
                    tokens[index].head._.is_entity:
                TokenizerUtils.clear_entity(tokens[index].head)

    @staticmethod
    def filter_on_entity_name_as_prepositional_complement(tokens):
        '''
        For utterance containing "types", "of", "crime" or "types", "of", "locations", the "crime" and "location"
        are entity slot names, the head of that is preposition "of" and the head of the preposition is the noun
        "types". So we merge this linguistic pattern into "types of crime", "types of location".
        '''
        synonyms_for_total = set(['total', 'number'])
        for lemmas in [synset.lemmas() for synset in wn.synsets('total', pos=wn.NOUN)]:
            for lemma in lemmas:
                synonyms_for_total.add(lemma.name())

        target_spans = []
        for token in tokens:
            if not token._.is_entity:
                continue

            if not token._.is_entity_name:
                continue

            if token.head.pos_ != 'ADP':
                continue

            if token.head.text.lower() != 'of':
                continue

            if token.head.head.pos_ != 'NOUN':
                continue

            if token.head.head.text in synonyms_for_total:
                TokenizerUtils.clear_entity(token)
                continue

            start = token.head.head._.start_char
            end = token._.end_char

            target_spans.append((token.head.head, token.head.head._.start_char, token, token._.end_char))

        for start_token, start, end_token, end in target_spans:
            EntityDependencyFilter.update_entity_info(start_token, start, end_token, end)

        try:
            TokenizerUtils.merge_tokens(
                doc=tokens,
                token_spans=TokenizerUtils.get_non_overlapping_token_spans_from_char_spans(
                    doc=tokens,
                    char_spans=[(start, end) for _, start, _, end in target_spans]
                )
            )
        except Exception as e:
            print("Error merging text", tokens.text)
            raise e

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
    def apply_subject_verb_object(doc):
        svos = []
        for subj, verb, obj in findSVOs(doc):
            svos.append((subj, verb, obj))

        return svos

    def __call__(self, doc):
        if not doc:
            return doc

        # Get the dependency tree in node class representation for easier tree traversal
        parsed_dependencies = DependencyParser.parse(doc=doc)

        # Get the prepositional phrases and for any temporal based prep phrases with more than one
        # noun prepositional complement and is temporal entity slot, we disambiguate by only
        # counting the first prepositional complement and merging that whole phrase as one token.
        # Example: "by","months","of","the","year" would merge into "by","months of the year" and
        # the entity slots would be ("by",None) and ("months of the year",month).
        prepositional_phrases = EntityDependencyFilter.get_phrases(parsed_dependencies, pos='ADP')
        EntityDependencyFilter.filter_on_multiple_temporal_prepositional_complements(
            prepositional_phrases, doc)

        # For situations such as "types","of","crime" and "types","of","locations" where we have "crime" and
        # "locations" as entity slot names, and the head of the head word ("types") is a Noun, we merge these
        # to obtain ("types of crimes","crime") and "types of locations","location")
        EntityDependencyFilter.filter_on_entity_name_as_prepositional_complement(doc)

        # Get all adjective phrases and if the adjective is "total" and the word being described is
        # an entity slot name, then clear the entity slot name. For example "total","crimes" would have entity
        # slots ("total",None), ("crimes","crime"). After processing it will be ("total",None),("crimes",None)
        adj_phrases = EntityDependencyFilter.get_phrases(parsed_dependencies, pos='ADJ')

        EntityDependencyFilter.filter_on_entities_modified_by_total_adjective(adj_phrases)

        '''for i, phrase in enumerate(prepositional_phrases):
            print('PREPPHRASE',i,phrase)
            print('\n')

        for i, phrase in enumerate(EntityDependencyFilter.get_phrases(parsed_dependencies, pos='NOUN')):
            print('NOUNPHRASE',i,phrase)
            print('\n')'''

        return doc
