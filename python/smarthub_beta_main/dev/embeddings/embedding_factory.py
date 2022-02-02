from .bert_embedding import BertEmbedding
from .word2vec_embedding import Word2VecEmbedding


class EmbeddingFactory:
    @staticmethod
    def build(config):
        if config['use_embedding'] == 'word2vec':
            return Word2VecEmbedding(config)
        elif config['use_embedding'] == 'bert':
            return BertEmbedding(config)
        return None
