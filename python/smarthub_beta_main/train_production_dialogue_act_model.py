import os
os.environ['CUDA_VISIBLE_DEVICES'] = '0'
os.environ["OMP_NUM_THREADS"] = '4'
os.environ["OPENBLAS_NUM_THREADS"] = '5'
os.environ["MKL_NUM_THREADS"] = '6'
os.environ["VECLIB_MAXIMUM_THREADS"] = '4'
os.environ["NUMEXPR_NUM_THREADS"] = '6'
os.environ["NUMEXPR_NUM_THREADS"] = '5'

from dev.dialogue_act_model.crf_model import CRFModel as DACRFModel
from dev.dialogue_act_model.utils import ClassificationLevelConfig
from dev.referring_expression_extraction_model.utils import UseEmbeddingConfig

dialogue_act_factory = DACRFModel()
for top_unseen_subjects, top_dialogue_act_model, bottom_unseen_subjects, bottom_dialogue_act_model in dialogue_act_factory.train(
        classification_level=ClassificationLevelConfig.TWO_LEVEL,
        k_cross_validation=-1,
        augment_with_paraphrases=True,
        augment_with_slot_replacement=True,
        augment_with_synonym_replacement=False,
        embedding_type=UseEmbeddingConfig.USE_CRIME_EMBEDDING,
        total_versions=10,
        max_sequence_length=40,
        max_queries=20,
        iterations=20,
        evaluate=False):
    print("Completed training top DA model", top_dialogue_act_model, "and bottom DA model", bottom_dialogue_act_model,
          "for production")
