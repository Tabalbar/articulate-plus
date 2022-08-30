import numpy as np


class SequenceOfSequenceFeatureVectors:
    def __init__(self, feature_extractor):
        self.feature_extractor = feature_extractor

    def extract(self,
                corpus_path,
                tokenize=False,
                include_setup=True,
                include_request=True,
                include_conclusion=True,
                include_surrounding=True,
                include_unigrams=True,
                include_tag=True,
                include_pos=True,
                include_dep=True,
                include_tag_unigrams=True,
                include_pos_unigrams=True,
                include_dep_unigrams=True,
                include_avg_word_embeddings=True,
                include_utt_length=True,
                include_sentiment=True,
                include_number_of_slots=True,
                include_number_of_non_modal_verbs=True,
                include_number_of_wh_words=True,
                IGNORE_CLASSES=['appearance', 'big high level question'],
                MERGE_CLASSES=['createvis', 'modifyvis'],
                is_corpus_json=False,
                total_versions=50):
        corpus = self.feature_extractor.get_corpus(
            corpus_path=corpus_path,
            tokenize=tokenize,
            include_setup=include_setup,
            include_request=include_request,
            include_conclusion=include_conclusion,
            is_corpus_json=is_corpus_json,
            total_versions=total_versions)

        all_subject_names, all_utterances, all_features, all_utterance_types, \
        subject_name_by_index = \
            self.feature_extractor.create_context_features(
                corpus=corpus,
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
                include_number_of_wh_words=include_number_of_wh_words,
                IGNORE_CLASSES=IGNORE_CLASSES,
                MERGE_CLASSES=MERGE_CLASSES)

        X_raw = []
        X_utterances = []
        y_raw = []

        CLASSES = []

        context_features = zip(all_subject_names, all_utterances, all_features, all_utterance_types)
        for subject_name, utterances, features, utterance_type in context_features:
            CLASSES += utterance_type
            X_raw.append(features)
            y_raw.append(utterance_type)

            X_utterances.append(utterances)

        CLASSES = np.unique(CLASSES)
        tag_to_index = {str(CLASSES[i]): i for i in range(len(CLASSES))}
        index_to_tag = {idx: tag for tag, idx in tag_to_index.items()}

        return subject_name_by_index, X_raw, y_raw, CLASSES, X_utterances, tag_to_index, index_to_tag
