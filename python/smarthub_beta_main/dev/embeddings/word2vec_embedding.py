import gensim
import numpy as np

from .embedding import Embedding


class Word2VecEmbedding(Embedding):
    def __init__(self, config):
        super().__init__(config=config)

        if config['train']:
            self._window = config['train']['window']
            self._min_count = config['train']['min_count']
            self._workers = config['train']['workers']

    def partially_contains(self, sentence, token):
        text, token_start_char = token

        if self.embedding_model.wv.__contains__(text):
            return True

        for word in text.split():
            if self.embedding_model.wv.__contains__(word):
                return True
        return False

    def contains(self, sentence, text):
        return self.embedding_model.wv.__contains__(text)

    def get_token_embedding(self, sentence, token):
        return self._get_sub_token_embedding(None, (token, -1))

    def get_all_token_embeddings(self, sentences, tokens):
        if self._verbose:
            print("Verbose: Started retrieving embeddings for", len(tokens), "tokens")

        token_embeddings = []
        for idx, (sentence, token) in enumerate(zip(sentences, tokens)):
            token_embeddings.append(self.get_token_embedding(sentence, token))

        token_embeddings = np.vstack(np.asarray(token_embeddings))
        if self._verbose:
            print("Verbose: Completed retrieving", token_embeddings.shape, "token embeddings")
        return token_embeddings

    def _get_sub_token_embedding(self, sentence, token):
        text, token_start_char = token
        if self.contains(sentence, text):
            return self.embedding_model.wv.__getitem__(text)

        sub_word_embedding = []
        for word in text.split():
            if self.embedding_model.wv.__contains__(word):
                sub_word_embedding.append(self.embedding_model.wv.__getitem__(word))

        if sub_word_embedding:
            token_embedding = np.average(sub_word_embedding, axis=0)
            return token_embedding

        return np.zeros((self._dims,))

    def get_sentence_embedding(self, sentence, only_important_phrases=False):
        word_embeddings = []
        for idx, token in enumerate(sentence):
            if only_important_phrases:
                if token._.is_important_phrase:
                    continue

            token_embedding = self._get_sub_token_embedding(sentence, token)
            if token_embedding is not None:
                word_embeddings.append(token_embedding)

        if word_embeddings:
            return np.average(word_embeddings, axis=0)

        return np.zeros((self._dims,))

    def get_all_sentence_embeddings(self, sentences, only_important_phrases=False):
        if self._verbose:
            print("Verbose: Started retrieving embeddings for", len(sentences), "sentences")

        sentence_embeddings = []
        for idx, sentence in enumerate(sentences):
            sentence_embedding = self.get_sentence_embedding(sentence, only_important_phrases)
            sentence_embeddings.append(sentence_embedding)
            if self._verbose:
                print("Verbose: retrieved", int(np.asarray(sentence_embeddings).shape[0] / self._dims),
                      "sentences embeddings out of", len(sentences), "total sentences")
        sentence_embeddings = np.vstack(np.asarray(sentence_embeddings)).reshape(-1, self._dims)

        if self._verbose:
            print("Verbose: Completed retrieving", sentence_embeddings.shape, "sentence embeddings")

        return sentence_embeddings  # shape is (batch_size X 100)

    def fit(self, X, y=None):
        # Note: MIN_COUNT implies that a token in the text must appear a minimum of MIN_COUNT=5 times to be used by
        # the word2vec model, otherwise it is ignored
        if self._verbose:
            print("Verbose: Started training embeddings for the", self._model_name, "model")
        self.embedding_model = gensim.models.Word2Vec(X, size=self._dims, window=self._window,
                                                      min_count=self._min_count, workers=self._workers)
        if self._verbose:
            print("Verbose: Started training embeddings for the", self._model_name, "model")

    def save(self, file_name=None):
        save_to = None
        if file_name:
            save_to = file_name
        elif self._model_name:
            save_to = self._embedding_model_path + self._model_name + '.pkl'

        if self._verbose:
            print("Verbose: Started saving embeddings to", save_to)
        self.embedding_model.save(save_to)
        if self._verbose:
            print("Verbose: Completed saving embeddings to", save_to)

    def load(self, file_name=None):
        load_from = None
        if file_name:
            load_from = file_name
        elif self._model_name:
            load_from = self._embedding_model_path + self._model_name + '.pkl'

        if load_from:
            if self._verbose:
                print("Verbose: Started loading embeddings from", load_from)
            try:
                self.embedding_model = gensim.models.Word2Vec.load(load_from)
            except FileNotFoundError:
                print("Verbose: Could not find file", load_from)

                load_from = '/'.join(file_name.split('/')[:-1]) + '/word2vec.glove.6b.100d.pkl'
                print("Verbose: Loading from pretrained model instead",load_from)
                self.embedding_model = gensim.models.KeyedVectors.load(load_from, mmap='r')

            if self._verbose:
                print("Verbose: Completed loading embeddings from", load_from)
        else:
            print("Verbose: Could not load.")
