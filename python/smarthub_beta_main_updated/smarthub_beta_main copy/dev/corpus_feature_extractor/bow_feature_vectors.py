import numpy as np
import scipy
from sklearn.feature_extraction.text import TfidfVectorizer


class BOWFeatureVectors:
    def __init__(self, feature_extractor):
        self.feature_extractor = feature_extractor

    def _tokenizer(self, text):
        return text.split(';')

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

        all_subject_names, all_utterances, all_features, all_utterance_types, all_utterance_types_sequence, \
        subject_name_by_index, subject_name_by_sequence = \
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
                IGNORE_CLASSES=['appearance', 'big high level question'],
                MERGE_CLASSES=['createvis', 'modifyvis'])

        X_raw = []
        X_utterances = []
        y_raw = []
        y_raw_sequence = all_utterance_types_sequence

        X_we = None
        X_utt_length = None
        X_sentiment = None
        X_number_of_slots = None
        X_number_of_non_modal_verbs = None
        X_number_of_wh_words = None

        context_features = zip(all_subject_names, all_utterances, all_features, all_utterance_types)
        for subject_name, utterances, features, utterance_type in context_features:

            if utterance_type in IGNORE_CLASSES:
                continue

            if type(utterances) != list:
                processed_utterances = [utterances]
            else:
                processed_utterances = utterances

            if include_avg_word_embeddings:
                we = self.feature_extractor.get_average_word_embeddings(utterances=processed_utterances)
                if len(we.shape) == 0:
                    continue
                if X_we is None:
                    X_we = []
                X_we.append(we)

            if include_utt_length:
                avg_utt_length = self.feature_extractor.get_average_utt_length(utterances=processed_utterances)
                if X_utt_length is None:
                    X_utt_length = []
                X_utt_length.append(avg_utt_length)

            if include_sentiment:
                avg_sentiment = self.feature_extractor.get_average_sentiment(utterances=processed_utterances)
                if X_sentiment is None:
                    X_sentiment = []
                X_sentiment.append(avg_sentiment)

            if include_number_of_slots:
                avg_number_of_slots = self.feature_extractor.get_average_number_of_slots(
                    utterances=processed_utterances)
                if X_number_of_slots is None:
                    X_number_of_slots = []
                X_number_of_slots.append(avg_number_of_slots)

            if include_number_of_non_modal_verbs:
                avg_number_of_non_modal_verbs = self.feature_extractor.get_average_number_of_non_modal_verbs(
                    utterances=processed_utterances)
                if X_number_of_non_modal_verbs is None:
                    X_number_of_non_modal_verbs = []
                X_number_of_non_modal_verbs.append(avg_number_of_non_modal_verbs)

            if include_number_of_wh_words:
                avg_number_of_wh_words = self.feature_extractor.get_average_number_of_wh_words(
                    utterances=processed_utterances)
                if X_number_of_wh_words is None:
                    X_number_of_wh_words = []
                X_number_of_wh_words.append(avg_number_of_wh_words)

            token_split = ';'
            X_utterances.append(utterances)
            X_raw.append(token_split.join(features))

            if utterance_type in MERGE_CLASSES:
                y_raw.append('merged')
            else:
                y_raw.append(utterance_type)

        # le = LabelEncoder()
        # CLASSES = np.unique(y_raw)
        # le.fit(CLASSES)
        # y = le.transform(y_raw)
        CLASSES = np.unique(y_raw)
        tag_to_index = {str(CLASSES[i]): i for i in range(len(CLASSES))}
        index_to_tag = {idx: tag for tag, idx in tag_to_index.items()}
        y = np.asarray([tag_to_index[i] for i in y_raw])

        vectorizer = TfidfVectorizer(tokenizer=self._tokenizer, ngram_range=(1, 3))
        tfidf = vectorizer.fit(X_raw)
        X_tfidf = tfidf.transform(X_raw)

        X_numerical = self.feature_extractor.create_numerical_features(
            X_we=X_we,
            X_sentiment=X_sentiment,
            X_utt_length=X_utt_length,
            X_number_of_slots=X_number_of_slots,
            X_number_of_non_modal_verbs=X_number_of_non_modal_verbs,
            X_number_of_wh_words=X_number_of_wh_words)

        if X_tfidf is not None and X_numerical is not None:
            X = scipy.sparse.hstack((X_tfidf, X_numerical), format='csr')
        elif X_tfidf is not None:
            X = X_tfidf
        else:
            X = X_numerical

        return subject_name_by_index, subject_name_by_sequence, \
               X_raw, y_raw, y_raw_sequence, CLASSES, X_utterances, X, y, \
               tfidf, tag_to_index, index_to_tag