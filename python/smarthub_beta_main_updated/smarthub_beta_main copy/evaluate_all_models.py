import os
os.environ['CUDA_VISIBLE_DEVICES'] = '0'
os.environ["OMP_NUM_THREADS"] = '4'
os.environ["OPENBLAS_NUM_THREADS"] = '5'
os.environ["MKL_NUM_THREADS"] = '6'
os.environ["VECLIB_MAXIMUM_THREADS"] = '4'
os.environ["NUMEXPR_NUM_THREADS"] = '6'
os.environ["NUMEXPR_NUM_THREADS"] = '5'

from dev.dialogue_act_model.utils import ClassificationLevelConfig
from dev.dialogue_act_model.utils import UseEmbeddingConfig as DAEmbeddingConfig
from dev.referring_expression_extraction_model.utils import UseEmbeddingConfig as REEmbeddingConfig
from eval.dialogue_act_model_evaluator import DialogueActModelEvaluator
from eval.text_segmentation_model_evaluator import TextSegmentationModelEvaluator
from eval.referring_expression_extraction_model_evaluator import ReferringExpressionExtractionModelEvaluator
from eval.smarthub_evaluator import SmarthubEvaluator

from copy import copy
config = {
    'training_parameters': {
        'k_cross_validation': 5,
        'max_sequence_length': 40,
        'max_queries': 20,
        'batch_size': None,
        'classification_level': ClassificationLevelConfig.TWO_LEVEL
    },

    'embedding_parameters': {
        'embedding_dim': 100,
        'embedding_type': DAEmbeddingConfig.USE_CRIME_EMBEDDING
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

refexp_config = copy(config)
refexp_config['training_parameters']['max_sequence_length'] = 20
refexp_config['embedding_parameters']['embedding_type'] = REEmbeddingConfig.USE_CRIME_EMBEDDING
for evaluator in [
        DialogueActModelEvaluator(config),
        TextSegmentationModelEvaluator(config),
        SmarthubEvaluator(config),
        ReferringExpressionExtractionModelEvaluator(refexp_config)
    ]:
    evaluator.evaluate()