from ..rule import Rule
from ..shared_established_reference_rules import Utilities

'''
- Step 3: create a visualization specification for current request.
- do not add to dialogue history until discourse determination is made in subsequent steps.

gold data:
1. curr_spec (shared utility).
2. curr_spec gesture target id  (shared utility).
3. curr_spec history  (shared utility).
'''


class VisualizationSpecificationCreationRule(Rule):
    def __init__(self):
        super().__init__()

    def execute(self, rule_context):
        # create specification based on gold referring expression + gold dialogue act + gold gesture target vis id.
        # - avoid propagation error: use gold inputs since we want to build a gold dialogue history.
        # - otherwise when comparing effectiveness of our reference resolution approach, hard to tell if
        #   result is because of bad reference resolution approach or bad dialogue history.
        rule_context.curr_spec.spec = Utilities.create_visualization_specification(
            rule_context=rule_context,
            referring_expression=rule_context.request.gold_referring_expression.referring_expression_info,
            dialogue_act=rule_context.request.gold_dialogue_act,
            gesture_target_vis_id=rule_context.request.gold_gesture_reference.target_vis_id)

    def should_execute(self, rule_context):
        return True
