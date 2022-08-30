from app import LanguageUnderstandingModels
from ..rule import Rule
from ..shared_language_model_prediction_rules import Utilities
from run.offline_mode.statistics import Statistics

'''
- Step 2: prediction of the language models (i.e., dialogue acts + referring expression extraction).

gold data:
1. dialogue act.

predicted data:
1  referring expression (shared utility).
2. dialogue act.

statistics:
1. compare gold gold dialogue act to predicted dialogue act.
'''


class ReferringExpressionPredictionRule(Rule):
    def __init__(self):
        super().__init__()

    def execute(self, rule_context):
        predicted_referring_expressions = LanguageUnderstandingModels.predict_referring_expressions(
            utterance=rule_context.request.utterance, fold=rule_context.FOLD)

        rule_context.request.pred_referring_expression.referring_expression_info, \
            rule_context.request.pred_referring_expression.text = \
            Utilities.process_referring_expression(
                rule_context=rule_context,
                predicted_referring_expressions=predicted_referring_expressions)

    def should_execute(self, rule_context):
        return True


class DialogueActPredictionRule(Rule):
    def __init__(self):
        super().__init__()

    def execute(self, rule_context):
        # predict dialogue act using gold gesture target vis id + gold referring expression.
        # - avoid error propagation: use gold inputs rather than predicted inputs.
        # - otherwise when comparing to gold dialogue act, hard to tell if result is because of
        #   bad model or bad input to the model (only want to compare if model is good or bad).
        rule_context.request.pred_dialogue_act = \
            Utilities.predict_dialogue_act(
                rule_context=rule_context,
                gesture_target_vis_id=rule_context.request.gold_gesture_reference.target_vis_id,
                referring_expression=rule_context.request.gold_referring_expression.text,
                fold=rule_context.FOLD)

    def should_execute(self, rule_context):
        return True


class DialogueActExtractionRule(Rule):
    def __init__(self):
        super().__init__()

    def execute(self, rule_context):
        # extract gold dialogue act.
        rule_context.request.gold_dialogue_act = \
            ['merged', rule_context.request.utterance_component.get_utterancetype_attribute()]

    def should_execute(self, rule_context):
        return True


class DialogueActStatisticsRule(Rule):
    def __init__(self):
        super().__init__()

    def execute(self, rule_context):
        top_level_distribution = Statistics.top_level_dialogue_acts_match_distribution.distributions[-1]

        top_level_distribution.total_labels += 1
        if rule_context.request.gold_dialogue_act[0] == 'nonmerged' and \
                rule_context.request.pred_dialogue_act[0] == 'nonmerged':
            top_level_distribution.total_labels_matched += 1
        elif rule_context.request.gold_dialogue_act[0] == 'merged' and \
                rule_context.request.pred_dialogue_act[0] == 'merged':
            top_level_distribution.total_labels_matched += 1

            bottom_level_distribution = Statistics.bottom_level_dialogue_acts_match_distribution.distributions[-1]

            bottom_level_distribution.total_labels += 1
            if rule_context.request.gold_dialogue_act[1] in \
                    ['preference', 'factbased', 'clarification'] and \
                    rule_context.request.pred_dialogue_act[1] in \
                    ['preference', 'factbased', 'clarification']:
                bottom_level_distribution.total_labels_matched += 1
            elif rule_context.request.gold_dialogue_act[1] == \
                    rule_context.request.pred_dialogue_act[1]:
                bottom_level_distribution.total_labels_matched += 1

    def should_execute(self, rule_context):
        return True
