from ..rule import Rule
from ..shared_established_reference_rules import Utilities

'''
- Step 3: create a visualization specification for current request.
- do not add to dialogue history until discourse determination is made in subsequent steps.

predicted data:
1. curr_spec (shared utility).
2. curr_spec gesture target id  (shared utility).
3. curr_spec history  (shared utility).
'''


class VisualizationSpecificationCreationRule(Rule):
    def __init__(self):
        super().__init__()

    def execute(self, rule_context):
        # create specification.
        rule_context.curr_spec.spec = Utilities.create_visualization_specification(
            rule_context=rule_context,
            referring_expression=rule_context.request.pred_referring_expression.referring_expression_info,
            dialogue_act=rule_context.request.pred_dialogue_act,
            gesture_target_vis_id=rule_context.context.gesture_target_vis_ids[-1])

    def should_execute(self, rule_context):
        return True
