import abc
import re
from abc import ABCMeta

import numpy as np
import scipy
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from scipy.sparse.csr import csr_matrix
from sklearn.preprocessing import normalize


class FeatureExtractor(metaclass=ABCMeta):
    __metaclass__ = abc.ABCMeta

    def __init__(self, corpus_entity_extractor):
        self.corpus_entity_extractor = corpus_entity_extractor
        self.embedding_model = self.corpus_entity_extractor.get_embedding_model()
        self.embedding_dim = self.embedding_model.get_dimensions()
        self.sentiment_analyzer = SentimentIntensityAnalyzer()

    @abc.abstractmethod
    def get_corpus(self, corpus_path, include_setup=True, include_request=True, include_conclusion=True,
                   tokenize_as_text=False, tokenize=True, tokenized_split=';', is_corpus_json=False, total_versions=50):
        pass

    @abc.abstractmethod
    def create_text_features(
            self,
            utterance,
            prefix_label,
            include_unigrams=True,
            include_tag=True,
            include_pos=True,
            include_dep=True,
            include_tag_unigrams=True,
            include_pos_unigrams=True,
            include_dep_unigrams=True):
        pass

    @abc.abstractmethod
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
        pass

    @abc.abstractmethod
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
            include_dep_unigrams=True):
        pass

    @abc.abstractmethod
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
                                include_avg_word_embeddings=True,
                                include_utt_length=True,
                                include_sentiment=True,
                                include_number_of_slots=True,
                                include_number_of_non_modal_verbs=True,
                                include_number_of_wh_words=True,
                                IGNORE_CLASSES=['appearance', 'big high level question'],
                                MERGE_CLASSES=['createvis', 'modifyvis']):
        pass

    @staticmethod
    def transform_to_sparse_vector(X_source, normalizer='max', is_already_array=False):
        if not is_already_array:
            return normalize(csr_matrix(np.array(X_source).reshape(-1, 1)), norm=normalizer)
        else:
            return normalize(csr_matrix(X_source), norm=normalizer)

    @staticmethod
    def transform_to_sparse_vector_and_append(X_source, X_target, is_already_array=False, normalizer='max'):
        X_source_norm = FeatureExtractor.transform_to_sparse_vector(X_source=X_source, normalizer=normalizer)
        X_target = scipy.sparse.hstack((X_target, X_source_norm), format='csr')
        return X_target

    def get_average_utt_length(self, utterances):
        if len(utterances) == 0:
            return 0.0

        lst = []
        for utterance in utterances:
            utt_length = len(utterance)
            lst.append(utt_length)
        avg_utt_length = np.mean(lst, axis=0)
        return avg_utt_length

    def get_average_sentiment(self, utterances):
        if len(utterances) == 0:
            return 0.0

        lst = []
        for utterance in utterances:
            sentiment = self.sentiment_analyzer.polarity_scores(utterance.text)['compound']
            lst.append(abs(sentiment))
        avg_sentiment = np.mean(lst, axis=0)
        return avg_sentiment

    def get_average_number_of_slots(self, utterances):
        if len(utterances) == 0:
            return 0.0
        lst = []
        for utterance in utterances:
            lst.append(len(utterance._.entities))
        avg_number_of_slots = np.mean(lst, axis=0)
        return avg_number_of_slots

    def get_average_number_of_non_modal_verbs(self, utterances):
        if len(utterances) == 0:
            return 0.0

        lst = []
        for utterance in utterances:
            cnt = 0
            for token in utterance:
                if token.pos_ == 'VERB' and token.tag_ != 'MD':
                    cnt += 1
            lst.append(cnt)
        avg_non_modal_verbs = np.mean(lst, axis=0)
        return avg_non_modal_verbs

    def get_average_number_of_wh_words(self, utterances):
        if len(utterances) == 0:
            return 0.0

        lst = []
        for utterance in utterances:
            cnt = 0
            for token in utterance:
                if token.pos_ == 'NOUN' and token.tag_ == 'WP':
                    cnt += 1
            lst.append(cnt)
        avg_number_of_wh_words = np.mean(lst, axis=0)
        return avg_number_of_wh_words

    def get_embedding_weights_by_index(self, vocab_size, word_to_index):
        embedding_model = self.embedding_model.embedding_model
        embedding_weights = np.zeros((vocab_size + 1, self.embedding_dim))
        for word, idx in word_to_index.items():
            if word in embedding_model.wv.vocab:
                embedding_weights[idx] = embedding_model.wv[word]
            else:
                phrase = word.split()

                if len(phrase) < 2:
                    embedding_weights[idx] = np.zeros((self.embedding_dim,))
                else:
                    phrase_lst = []
                    for phrase_word in phrase:
                        if phrase_word in embedding_model.wv.vocab:
                            phrase_lst.append(embedding_model.wv[phrase_word])
                        else:
                            phrase_lst.append(np.zeros((self.embedding_dim,)))
                    embedding_weights[idx] = np.mean(phrase_lst, axis=0)
        return embedding_weights

    def get_average_word_embeddings(self, utterances):
        if len(utterances) == 0:
            return np.zeros((self.embedding_dim,))

        embedding_model = self.embedding_model.embedding_model

        lst = []
        for utterance in utterances:
            for token in utterance:
                word = token.text
                if word in embedding_model.wv.vocab:
                    lst.append(embedding_model.wv[word])
                    continue

                phrase = word.split()
                if len(phrase) < 2:
                    lst.append(np.zeros((self.embedding_dim,)))
                    continue

                phrase_lst = []
                for phrase_word in phrase:
                    if phrase_word in embedding_model.wv.vocab:
                        phrase_lst.append(embedding_model.wv[phrase_word])
                    else:
                        phrase_lst.append(np.zeros((self.embedding_dim,)))
                lst.append(np.mean(phrase_lst, axis=0))
        avg_word_embeddings = np.mean(lst, axis=0)

        return avg_word_embeddings

    def get_subject_id(self, subject_name):
        span = re.search('\\d{1,2}$', subject_name.split('_')[0]).span()
        return int(subject_name[span[0]:span[1]])

    def update_subject_mapping(self, subject_name, subject_mapping, curr_idx, next_idx):
        subject_id = self.get_subject_id(subject_name)
        if subject_id not in subject_mapping:
            subject_mapping[subject_id] = []
        subject_mapping[subject_id].append(range(curr_idx, next_idx))
