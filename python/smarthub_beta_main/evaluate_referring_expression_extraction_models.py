import os
os.environ['CUDA_VISIBLE_DEVICES'] = '0'
os.environ["OMP_NUM_THREADS"] = '4'
os.environ["OPENBLAS_NUM_THREADS"] = '5'
os.environ["MKL_NUM_THREADS"] = '6'
os.environ["VECLIB_MAXIMUM_THREADS"] = '4'
os.environ["NUMEXPR_NUM_THREADS"] = '6'
os.environ["NUMEXPR_NUM_THREADS"] = '5'

from dev.referring_expression_extraction_model.utils import UseEmbeddingConfig as REEmbeddingConfig
from eval.referring_expression_extraction_model_evaluator import ReferringExpressionExtractionModelEvaluator


config = {
    'training_parameters': {
        'k_cross_validation': 5,
        'max_sequence_length': 20,
        'max_queries': 20,
        'batch_size': 1024,
        'classification_level': None
    },

    'embedding_parameters': {
        'embedding_dim': 100,
        'embedding_type': REEmbeddingConfig.USE_CRIME_EMBEDDING
    },

    'data_augmentation_parameters': {
        'augment_with_paraphrases': True,
        'augment_with_slot_replacement': True,
        'augment_with_synonym_replacement': False,
        'total_versions': 10
    },

    'dialogue_history_parameters': {
        'search_window_sizes': [0, 1, -1]
    },

    'dialogue_act_parameters': {
        'use_full_context_window': False
    }
}
evaluator = ReferringExpressionExtractionModelEvaluator(config)
evaluator.evaluate()
