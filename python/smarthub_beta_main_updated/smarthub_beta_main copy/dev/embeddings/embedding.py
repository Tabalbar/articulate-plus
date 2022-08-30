import abc
from abc import ABCMeta, abstractmethod


class Embedding(metaclass=ABCMeta):
    __metaclass__ = abc.ABCMeta

    def __init__(self, config):
        self._dims = config['dims']
        self._model_name = config['embedding_model_name']
        self._verbose = config['verbose']
        self._model_path = config['embedding_model_path']

    def get_dimensions(self):
        return self._dims

    @abstractmethod
    def partially_contains(self, sentence, token):
        pass

    @abstractmethod
    def contains(self, sentence, token):
        pass

    @abstractmethod
    def get_all_token_embeddings(self, sentences, tokens):
        pass

    @abstractmethod
    def get_all_sentence_embeddings(self, sentences, only_important_phrases=False):
        pass

    @abstractmethod
    def get_token_embedding(self, sentence, token):
        pass

    @abstractmethod
    def get_sentence_embedding(self, sentence, only_important_phrases=False):
        pass

    @abstractmethod
    def fit(self, X, y=None):
        pass

    @abstractmethod
    def save(self, file_name=None):
        pass

    @abstractmethod
    def load(self, file_name=None):
        pass
