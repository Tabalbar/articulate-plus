import numpy as np

from .corpus_feature_extractor_utils import CorpusFeatureExtractorUtils
from .feature_extractor import FeatureExtractor


class ContextBasedFeatureMaps(FeatureExtractor):
    def __init__(self, embedding_model_path, embedding_model_name):
        corpus_entity_extractor = CorpusFeatureExtractorUtils.get_context_based_corpus_entity_extractor(
            embedding_model_path=embedding_model_path, embedding_model_name=embedding_model_name)
        super().__init__(corpus_entity_extractor=corpus_entity_extractor)

    def get_corpus(self, corpus_path, include_setup=True, include_request=True, include_conclusion=True,
                   tokenize_as_text=False, tokenize=True, tokenized_split=';', is_corpus_json=False, total_versions=50):
        corpus = self.corpus_entity_extractor.extract(corpus_path=corpus_path, tokenize=tokenize,
                                                      is_corpus_json=is_corpus_json, total_versions=total_versions)

        contexts_by_subject_name = dict()
        for subject_name, subject_tokens in corpus:
            contexts = []
            for subject_token in subject_tokens:
                context = []
                utterance_type, tokenized_setups, tokenized_requests, tokenized_conclusions = \
                    subject_token[0], subject_token[1], subject_token[2], subject_token[3]

                if include_setup:
                    for utterance in tokenized_setups:
                        if tokenize_as_text:
                            context.append(([tokenized_split.join([token.text for token in utterance])], 'setup'))
                        else:
                            context.append(([utterance], 'setup'))

                if include_request:
                    for utterance in tokenized_requests:
                        if tokenize_as_text:
                            context.append(
                                ([tokenized_split.join([token.text for token in utterance])], utterance_type))
                        else:
                            context.append(([utterance], utterance_type))

                if include_conclusion:
                    for utterance in tokenized_conclusions:
                        if tokenize_as_text:
                            context.append(([tokenized_split.join([token.text for token in utterance])], 'conclusion'))
                        else:
                            context.append(([utterance], 'conclusion'))
                # Randomize [setup, request, conclusion] window, so for example it may become [request, conclusion, setup]
                # This may help CRF learn with better results

                # random.shuffle(context)
                contexts.append(context)

            contexts_by_subject_name[subject_name] = contexts

        return contexts_by_subject_name

    def create_text_features(
            self,
            utterance=None,
            prefix_label=None,
            include_unigrams=True,
            include_tag=True,
            include_pos=True,
            include_dep=True,
            include_tag_unigrams=True,
            include_pos_unigrams=True,
            include_dep_unigrams=True):

        feature_vector = dict()

        if include_unigrams:
            unigrams = {prefix_label + 'uni_' + token.text: token.text for token in utterance}
            feature_vector.update(unigrams)
        if include_tag:
            tag = {prefix_label + 'tag_' + token.tag_: token.tag_ for token in utterance}
            feature_vector.update(tag)
        if include_pos:
            pos = {prefix_label + 'pos_' + token.tag_: token.tag_ for token in utterance}
            feature_vector.update(pos)
        if include_dep:
            dep = {prefix_label + 'dep_' + token.dep_: token.dep_ for token in utterance}
            feature_vector.update(dep)
        if include_tag_unigrams:
            tag_unigrams = {prefix_label + 'uni_tag_' + token.text + '_' + token.tag_: token.text + '_' + token.tag_ for
                            token in utterance}
            feature_vector.update(tag_unigrams)
        if include_pos_unigrams:
            pos_unigrams = {prefix_label + 'uni_pos_' + token.text + '_' + token.pos_: token.text + '_' + token.pos_ for
                            token in utterance}
            feature_vector.update(pos_unigrams)
        if include_dep_unigrams:
            dep_unigrams = {prefix_label + 'uni_dep_' + token.text + '_' + token.dep_: token.text + '_' + token.dep_ for
                            token in utterance}
            feature_vector.update(dep_unigrams)

        return feature_vector

    def create_numerical_features(
            self,
            X_we,
            X_sentiment,
            X_utt_length,
            X_number_of_slots,
            X_number_of_non_modal_verbs,
            X_number_of_wh_words,
            utterance=None,
            prefix_label=None):

        feature_vector = dict()

        if X_we is not None:
            if len(utterance) > 0:
                pre_calc_avg_word_embeddings = X_we
            else:
                pre_calc_avg_word_embeddings = np.zeros((self.embedding_dim,))

            avg_word_embeddings = {prefix_label + 'avg_word_embedding_' + str(idx): vector_dim_value for
                                   idx, vector_dim_value in enumerate(
                    list(pre_calc_avg_word_embeddings))}

            feature_vector.update(avg_word_embeddings)

        if X_sentiment is not None:
            sentiment = {prefix_label + 'sentiment_' + str(0): X_sentiment}
            feature_vector.update(sentiment)

        if X_utt_length is not None:
            utt_length = {prefix_label + 'utt_length_' + str(0): X_utt_length}
            feature_vector.update(utt_length)

        if X_number_of_slots is not None:
            number_of_slots = {prefix_label + 'number_of_slots_' + str(0): X_number_of_slots}
            feature_vector.update(number_of_slots)

        if X_number_of_non_modal_verbs is not None:
            number_of_non_modal_verbs = {
                prefix_label + 'number_of_non_modal_verbs_' + str(0): X_number_of_non_modal_verbs}
            feature_vector.update(number_of_non_modal_verbs)

        if X_number_of_wh_words is not None:
            number_of_wh_words = {prefix_label + 'number_of_wh_words_' + str(0): X_number_of_wh_words}
            feature_vector.update(number_of_wh_words)

        return feature_vector

    def create_features_vector(
            self,
            utterances,
            index,
            include_surrounding=False,
            include_unigrams=True,
            include_tag=True,
            include_pos=True,
            include_dep=True,
            include_tag_unigrams=True,
            include_pos_unigrams=True,
            include_dep_unigrams=True,
            include_avg_word_embeddings=True,
            include_sentiment=True,
            include_utt_length=True,
            include_number_of_slots=True,
            include_number_of_non_modal_verbs=True,
            include_number_of_wh_words=True):

        feature_vector = dict()

        if index > 0 and include_surrounding:
            prev_utterance = utterances[index - 1]

            feature_vector.update(
                self.create_text_features(
                    utterance=prev_utterance,
                    prefix_label='-1:',
                    include_unigrams=include_unigrams,
                    include_tag=include_tag,
                    include_pos=include_pos,
                    include_dep=include_dep,
                    include_tag_unigrams=include_tag_unigrams,
                    include_pos_unigrams=include_pos_unigrams,
                    include_dep_unigrams=include_dep_unigrams))

            if include_avg_word_embeddings:
                X_we = self.get_average_word_embeddings(utterances=[prev_utterance])
            else:
                X_we = None
            if include_sentiment:
                X_sentiment = self.get_average_sentiment(utterances=[prev_utterance])
            else:
                X_sentiment = None
            if include_utt_length:
                X_utt_length = self.get_average_utt_length(utterances=[prev_utterance])
            else:
                X_utt_length = None
            if include_number_of_slots:
                X_number_of_slots = self.get_average_number_of_slots(utterances=[prev_utterance])
            else:
                X_number_of_slots = None
            if include_number_of_non_modal_verbs:
                X_number_of_non_modal_verbs = self.get_average_number_of_non_modal_verbs(utterances=[prev_utterance])
            else:
                X_number_of_non_modal_verbs = None
            if include_number_of_wh_words:
                X_number_of_wh_words = self.get_average_number_of_wh_words(utterances=[prev_utterance])
            else:
                X_number_of_wh_words = None

            feature_vector.update(
                self.create_numerical_features(
                    utterance=prev_utterance,
                    prefix_label='-1:',
                    X_we=X_we,
                    X_sentiment=X_sentiment,
                    X_utt_length=X_utt_length,
                    X_number_of_slots=X_number_of_slots,
                    X_number_of_non_modal_verbs=X_number_of_non_modal_verbs,
                    X_number_of_wh_words=X_number_of_wh_words))

        current_utterance = utterances[index]
        feature_vector.update(
            self.create_text_features(
                utterance=current_utterance,
                prefix_label='',
                include_unigrams=include_unigrams,
                include_tag=include_tag,
                include_pos=include_pos,
                include_dep=include_dep,
                include_tag_unigrams=include_tag_unigrams,
                include_pos_unigrams=include_pos_unigrams,
                include_dep_unigrams=include_dep_unigrams))

        if include_avg_word_embeddings:
            X_we = self.get_average_word_embeddings(utterances=[current_utterance])
        else:
            X_we = None
        if include_sentiment:
            X_sentiment = self.get_average_sentiment(utterances=[current_utterance])
        else:
            X_sentiment = None
        if include_utt_length:
            X_utt_length = self.get_average_utt_length(utterances=[current_utterance])
        else:
            X_utt_length = None
        if include_number_of_slots:
            X_number_of_slots = self.get_average_number_of_slots(utterances=[current_utterance])
        else:
            X_number_of_slots = None
        if include_number_of_non_modal_verbs:
            X_number_of_non_modal_verbs = self.get_average_number_of_non_modal_verbs(utterances=[current_utterance])
        else:
            X_number_of_non_modal_verbs = None
        if include_number_of_wh_words:
            X_number_of_wh_words = self.get_average_number_of_wh_words(utterances=[current_utterance])
        else:
            X_number_of_wh_words = None

        feature_vector.update(
            self.create_numerical_features(
                utterance=current_utterance,
                prefix_label='',
                X_we=X_we,
                X_sentiment=X_sentiment,
                X_utt_length=X_utt_length,
                X_number_of_slots=X_number_of_slots,
                X_number_of_non_modal_verbs=X_number_of_non_modal_verbs,
                X_number_of_wh_words=X_number_of_wh_words))

        return feature_vector

    def create_context_features(self,
                                corpus,
                                include_surrounding=True,
                                include_unigrams=True,
                                include_tag=True,
                                include_pos=True,
                                include_dep=True,
                                include_tag_unigrams=True,
                                include_pos_unigrams=True,
                                include_dep_unigrams=True,
                                include_avg_word_embeddings=False,
                                include_utt_length=False,
                                include_sentiment=False,
                                include_number_of_slots=False,
                                include_number_of_non_modal_verbs=False,
                                include_number_of_wh_words=False,
                                IGNORE_CLASSES=['appearance', 'big high level question'],
                                MERGE_CLASSES=['createvis', 'modifyvis']):

        all_utterances = []
        all_utterance_types = []
        all_features = []
        all_subject_names = []
        subject_name_by_index = dict()
        curr_idx = 0
        next_idx = 0
        for subject_name, contexts in corpus.items():
            for context in contexts:
                utterances = []
                utterance_types = []
                subject_names = []

                found_ignored_class = False
                for utterance, utterance_type in context:

                    if utterance_type in IGNORE_CLASSES:
                        found_ignored_class = True
                        utterances.clear()
                        utterance_types.clear()
                        subject_names.clear()
                        break

                    if utterance_type in MERGE_CLASSES:
                        utterance_type = 'merged'

                    utterances.append(utterance[0])
                    utterance_types.append(utterance_type)
                    subject_names.append(subject_name)

                if found_ignored_class:
                    continue

                if len(subject_names) > 0:
                    next_idx += 1
                else:
                    continue

                features = []
                for index, utterance in enumerate(utterances):
                    feature_vector = self.create_features_vector(
                        utterances=utterances,
                        index=index,
                        include_surrounding=include_surrounding,
                        include_unigrams=include_unigrams,
                        include_tag=include_tag,
                        include_pos=include_pos,
                        include_dep=include_dep,
                        include_tag_unigrams=include_tag_unigrams,
                        include_pos_unigrams=include_pos_unigrams,
                        include_dep_unigrams=include_dep_unigrams,
                        include_avg_word_embeddings=include_avg_word_embeddings,
                        include_utt_length=include_utt_length,
                        include_sentiment=include_sentiment,
                        include_number_of_slots=include_number_of_slots,
                        include_number_of_non_modal_verbs=include_number_of_non_modal_verbs,
                        include_number_of_wh_words=include_number_of_wh_words)

                    features.append(feature_vector)
                all_subject_names += subject_names
                all_utterances.append(utterances)
                all_features.append(features)
                all_utterance_types.append(utterance_types)

            self.update_subject_mapping(
                subject_name=subject_name,
                subject_mapping=subject_name_by_index,
                curr_idx=curr_idx,
                next_idx=next_idx)
            curr_idx = next_idx

        return all_subject_names, all_utterances, all_features, all_utterance_types, subject_name_by_index
