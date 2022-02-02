import string

import numpy as np
from sklearn.model_selection import KFold

from dev.dialogue_act_model.crf_model import CRFModel as DACRFModel
from dev.dialogue_act_model.utils import ClassificationLevelConfig, UseEmbeddingConfig
from dev.referring_expression_extraction_model.crf_model import CRFModel as RECRFModel
from dev.referring_expression_extraction_model.utils import UseEmbeddingConfig


class LanguageUnderstandingModels:
    K_CROSS_VALIDATION = 5
    TOTAL_SUBJECTS = 16

    _attribute_history = {}
    dialogue_act_factory = DACRFModel()
    dialogue_act_factory.train_init(
        classification_level=ClassificationLevelConfig.TWO_LEVEL,
        k_cross_validation=K_CROSS_VALIDATION,
        augment_with_paraphrases=True,
        augment_with_slot_replacement=True,
        augment_with_synonym_replacement=False,
        embedding_type=UseEmbeddingConfig.USE_CRIME_EMBEDDING,
        total_versions=10,
        max_sequence_length=40,
        max_queries=20,
        iterations=20,
        evaluate=False)

    top_dialogue_act_models = []
    bottom_dialogue_act_models = []

    referring_expression_extraction_factory = RECRFModel()
    referring_expression_models = []

    if K_CROSS_VALIDATION == -1:
        top_dialogue_act_models.append(
            dialogue_act_factory.load_model(which_level=ClassificationLevelConfig.TOP_LEVEL, subjects=None, fold=0))

        bottom_dialogue_act_models.append(
            dialogue_act_factory.load_model(which_level=ClassificationLevelConfig.BOTTOM_LEVEL, subjects=None, fold=0))

        referring_expression_models.append(
            referring_expression_extraction_factory.load_model(subjects=None, fold=0))
    else:
        k_fold = KFold(n_splits=K_CROSS_VALIDATION, shuffle=True, random_state=7)

        X_p = np.zeros((TOTAL_SUBJECTS,))
        y_p = np.zeros((TOTAL_SUBJECTS,))

        for fold, (train, test) in enumerate(k_fold.split(X_p, y_p)):
            top_dialogue_act_models.append(
                dialogue_act_factory.load_model(which_level=ClassificationLevelConfig.TOP_LEVEL, subjects=test,
                                                fold=fold))
            bottom_dialogue_act_models.append(
                dialogue_act_factory.load_model(which_level=ClassificationLevelConfig.BOTTOM_LEVEL,
                                                subjects=test, fold=fold))

            referring_expression_models.append(
                referring_expression_extraction_factory.load_model(subjects=test, fold=fold))

    @staticmethod
    def _get_attribute_mentions(utterance):
        attribute_mentions = []
        for entity, is_temporal, is_data_attribute in [
            (token._.entity, token._.is_temporal, token._.entity_data_attribute) for token in utterance if
            token._.entity or token._.is_temporal]:
            if not is_data_attribute:
                return attribute_mentions
            if is_temporal:
                attribute_mentions.append('time')
            else:
                attribute_mentions.append(entity)
        return attribute_mentions

    @staticmethod
    def predict_dialogue_act(context_utterances, gesture_target_id, referring_expressions, fold=0):
        dialogue_act_label = LanguageUnderstandingModels.dialogue_act_factory.predict(
            top_level_trained_model=LanguageUnderstandingModels.top_dialogue_act_models[fold],
            bottom_level_trained_model=LanguageUnderstandingModels.bottom_dialogue_act_models[fold],
            context_utterances=context_utterances)
        top_dialogue_act_label = dialogue_act_label.get_top_level()[0]
        bottom_dialogue_act_label = dialogue_act_label.get_bottom_level()[0]

        request_utterance = context_utterances[-1]

        if not request_utterance._.entities:
            return 'nonmerged', 'clarification'

        if top_dialogue_act_label != 'merged':
            return 'nonmerged', bottom_dialogue_act_label

        if gesture_target_id != -1 and referring_expressions and bottom_dialogue_act_label in ['createvis', 'merged']:
            bottom_dialogue_act_label = 'modifyvis'
        has_new_attribute_mentions = False
        for attribute_mention in LanguageUnderstandingModels._get_attribute_mentions(request_utterance):
            if attribute_mention not in LanguageUnderstandingModels._attribute_history:
                LanguageUnderstandingModels._attribute_history[attribute_mention] = True
                has_new_attribute_mentions = True

        if has_new_attribute_mentions:
            return top_dialogue_act_label, 'createvis'

        if bottom_dialogue_act_label == 'merged':
            return top_dialogue_act_label, 'modifyvis'

        return top_dialogue_act_label, bottom_dialogue_act_label

    @staticmethod
    def predict_referring_expressions(utterance, fold=0):
        referring_expressions = LanguageUnderstandingModels.referring_expression_extraction_factory.predict(
            trained_model=LanguageUnderstandingModels.referring_expression_models[fold], utterance=utterance)
        return referring_expressions
