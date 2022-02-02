from app import LanguageUnderstandingModels

import numpy as np

'''
- Step 2: prediction of the language models (i.e., dialogue acts + referring expression extraction).

1. predict dialogue act (shared utility).
2. predict referring expression (shared utility).
'''


class Utilities:
    @staticmethod
    def process_referring_expression(rule_context, predicted_referring_expressions):
        if not predicted_referring_expressions:
            return None, None

        referring_expression_info = predicted_referring_expressions[
            np.argmax([len(p.words) for p in predicted_referring_expressions])]

        text = [word.lower() for word in referring_expression_info.words]
        return referring_expression_info, text

    @staticmethod
    def predict_dialogue_act(rule_context, gesture_target_vis_id, referring_expression, fold=0):
        context_utterances = []
        if rule_context.USE_FULL_CONTEXT_WINDOW_FOR_DA_PREDICTION:
            for utterance in rule_context.setup.utterances:
                context_utterances.append(utterance)

        context_utterances.append(rule_context.request.utterance)

        return LanguageUnderstandingModels.predict_dialogue_act(
            context_utterances=context_utterances,
            gesture_target_id=gesture_target_vis_id,
            referring_expressions=referring_expression,
            fold=fold)
