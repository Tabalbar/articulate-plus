from ..rule import Rule
from ..shared_language_model_prediction_rules import Utilities

'''
- Step 2: prediction of the language models (i.e., dialogue acts + referring expression extraction).

predicted data:
1  referring expression (shared utility).
3. dialogue act.
'''


class ReferringExpressionPredictionRule(Rule):
    def __init__(self):
        super().__init__()

    def execute(self, rule_context):
        predicted_referring_expressions = rule_context.context.referring_expressions[-1]

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
        # predict dialogue act.
        rule_context.request.pred_dialogue_act = rule_context.context.dialogue_acts[-1]

    def should_execute(self, rule_context):
        return True
