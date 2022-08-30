from .corpus_feature_extractor_utils import CorpusFeatureExtractorUtils
from .feature_extractor import FeatureExtractor


class ContextBasedFeatureVectors(FeatureExtractor):
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

                # random.shuffle(context)
                contexts.append(context)

            contexts_by_subject_name[subject_name] = contexts

        return contexts_by_subject_name

    def create_text_features(
            self,
            utterance,
            prefix_label=None,
            include_unigrams=True,
            include_tag=True,
            include_pos=True,
            include_dep=True,
            include_tag_unigrams=True,
            include_pos_unigrams=True,
            include_dep_unigrams=True):

        feature_vector = []
        if include_unigrams:
            unigrams = [token.text for token in utterance]
            feature_vector += unigrams
        if include_tag:
            tag = [token.tag_ for token in utterance]
            feature_vector += tag
        if include_pos:
            pos = [token.pos_ for token in utterance]
            feature_vector += pos
        if include_dep:
            dep = [token.dep_ for token in utterance]
            feature_vector += dep
        if include_tag_unigrams:
            tag_unigrams = [token.text + '_' + token.tag_ for token in utterance]
            feature_vector += tag_unigrams
        if include_pos_unigrams:
            pos_unigrams = [token.text + '_' + token.pos_ for token in utterance]
            feature_vector += pos_unigrams
        if include_dep_unigrams:
            dep_unigrams = [token.text + '_' + token.dep_ for token in utterance]
            feature_vector += dep_unigrams

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

        X = None

        if X_we is not None:
            if X is None:
                X = FeatureExtractor.transform_to_sparse_vector(X_we, is_already_array=True, normalizer='l2')
            else:
                FeatureExtractor.transform_to_sparse_vector_and_append(X_source=X_we, X_target=X, is_already_array=True,
                                                                       normalizer='l2')

        if X_sentiment is not None:
            if X is None:
                X = FeatureExtractor.transform_to_sparse_vector(X_sentiment, normalizer='max')
            else:
                FeatureExtractor.transform_to_sparse_vector_and_append(X_source=X_sentiment, X_target=X,
                                                                       normalizer='max')

        if X_utt_length is not None:
            if X is None:
                X = FeatureExtractor.transform_to_sparse_vector(X_utt_length, normalizer='max')
            else:
                FeatureExtractor.transform_to_sparse_vector_and_append(X_source=X_utt_length, X_target=X,
                                                                       normalizer='max')

        if X_number_of_slots is not None:
            if X is None:
                X = FeatureExtractor.transform_to_sparse_vector(X_number_of_slots, normalizer='max')
            else:
                FeatureExtractor.transform_to_sparse_vector_and_append(X_source=X_number_of_slots, X_target=X,
                                                                       normalizer='max')

        if X_number_of_non_modal_verbs is not None:
            if X is None:
                X = FeatureExtractor.transform_to_sparse_vector(X_number_of_non_modal_verbs, normalizer='max')
            else:
                FeatureExtractor.transform_to_sparse_vector_and_append(X_source=X_number_of_non_modal_verbs, X_target=X,
                                                                       normalizer='max')

        if X_number_of_wh_words is not None:
            if X is None:
                X = FeatureExtractor.transform_to_sparse_vector(X_number_of_wh_words, normalizer='max')
            else:
                FeatureExtractor.transform_to_sparse_vector_and_append(X_source=X_number_of_wh_words, X_target=X,
                                                                       normalizer='max')

        return X

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
            include_avg_word_embeddings=False,
            include_sentiment=False,
            include_utt_length=False,
            include_number_of_slots=False,
            include_number_of_non_modal_verbs=False,
            include_number_of_wh_words=False):

        feature_vector = []
        if index > 0 and include_surrounding:
            prev_utterance = utterances[index - 1]
            feature_vector += \
                self.create_text_features(
                    prev_utterance,
                    include_unigrams=include_unigrams,
                    include_tag=include_tag,
                    include_pos=include_pos,
                    include_dep=include_dep,
                    include_tag_unigrams=include_tag_unigrams,
                    include_pos_unigrams=include_pos_unigrams,
                    include_dep_unigrams=include_dep_unigrams)

        current_utterance = utterances[index]
        feature_vector += \
            self.create_text_features(
                current_utterance,
                include_unigrams=include_unigrams,
                include_tag=include_tag,
                include_pos=include_pos,
                include_dep=include_dep,
                include_tag_unigrams=include_tag_unigrams,
                include_pos_unigrams=include_pos_unigrams,
                include_dep_unigrams=include_dep_unigrams)

        if index < len(utterances) - 1 and include_surrounding:
            next_utterance = utterances[index + 1]
            feature_vector += \
                self.create_text_features(
                    next_utterance,
                    include_unigrams=include_unigrams,
                    include_tag=include_tag,
                    include_pos=include_pos,
                    include_dep=include_dep,
                    include_tag_unigrams=include_tag_unigrams,
                    include_pos_unigrams=include_pos_unigrams,
                    include_dep_unigrams=include_dep_unigrams)

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
        all_utterance_types_sequence = []
        all_features = []
        all_subject_names = []
        subject_name_by_index = dict()
        subject_name_by_sequence = dict()
        curr_idx = 0
        next_idx = 0
        curr_seq_idx = 0
        next_seq_idx = 0
        for subject_name, contexts in corpus.items():
            for context in contexts:
                utterances = []
                utterance_types = []
                subject_names = []
                utterance_types_sequence = []

                found_ignored_class = False
                saved_next_idx = next_idx
                for utterance, utterance_type in context:
                    if utterance_type in IGNORE_CLASSES:
                        found_ignored_class = True
                        next_idx = saved_next_idx
                        break

                    if utterance_type in MERGE_CLASSES:
                        utterance_type = 'merged'

                    utterances.append(utterance[0])
                    utterance_types.append(utterance_type)
                    utterance_types_sequence.append(utterance_type)
                    subject_names.append(subject_name)
                    next_idx += 1

                if found_ignored_class:
                    continue

                if len(subject_names) == 0:
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
                    all_utterances.append(utterance)
                all_subject_names += subject_names
                all_features += features
                all_utterance_types += utterance_types

                if len(utterance_types_sequence) > 0:
                    all_utterance_types_sequence.append(utterance_types_sequence)

                    next_seq_idx = curr_seq_idx + len(utterance_types_sequence)
                    self.update_subject_mapping(
                        subject_name=subject_name,
                        subject_mapping=subject_name_by_sequence,
                        curr_idx=curr_seq_idx,
                        next_idx=next_seq_idx)
                    curr_seq_idx = next_seq_idx

            self.update_subject_mapping(
                subject_name=subject_name,
                subject_mapping=subject_name_by_index,
                curr_idx=curr_idx,
                next_idx=next_idx)
            curr_idx = next_idx

        return all_subject_names, all_utterances, all_features, all_utterance_types, \
               all_utterance_types_sequence, subject_name_by_index, subject_name_by_sequence
