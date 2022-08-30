from dev.embeddings import EmbeddingFactory
from model_paths import ModelPaths

import numpy as np
from scipy.spatial.distance import cosine


class StatisticsUtil:
    embedding_model_name = 'word2vec.100d.chicagocrimevis'
    EMBEDDING_CONFIG = {'use_embedding': 'word2vec',
                        'dims': 100,
                        'embedding_model_path': ModelPaths.WORD_EMBEDDING_MODELS_DIR,
                        'embedding_model_name': embedding_model_name,
                        'train': None,
                        'verbose': False}
    EMBEDDING_MODEL_PATH = ModelPaths.WORD_EMBEDDING_MODELS_DIR
    EMBEDDING_MODEL = EmbeddingFactory.build(EMBEDDING_CONFIG)
    EMBEDDING_MODEL.load(file_name=EMBEDDING_MODEL_PATH + embedding_model_name + '.pkl')

    # compare cosine similarity between two phrases.
    # particularly useful to compare gold referring expression text to predicted referring expression text.
    @staticmethod
    def phrase_cosine_similarity(phrase1, phrase2):
        concat = [[(t.text.lower(), t.idx) for t in phrase1],
                  [(t.text.lower(), t.idx) for t in phrase2]]
        res = StatisticsUtil.EMBEDDING_MODEL.get_all_sentence_embeddings(concat)

        if np.all(res[0] == 0) or np.all(res[1] == 0):
            return 0.0

        return 1 - cosine(res[0], res[1])
