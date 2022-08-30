from run.rule import Rule
from run.shared_discourse_extractor import SharedDiscourseExtractor

'''
- Step 4.1: process if the request is about creating a new vis from scratch (i.e., not from any template).

predicted data:
1. generate smarthub id.
2. curr_spec added to dialogue history (shared).
'''


class VisualizationSpecificationStateUpdateRule(Rule):
    def __init__(self):
        super().__init__()

    def execute(self, rule_context):
        # assign latest available smarthub id to curr_spec id.
        rule_context.curr_spec.spec.plot_headline.id = rule_context.CURR_DIALOGUE_HISTORY.history_id

    def should_execute(self, rule_context):
        # check if discourse type is creating new vis from scratch (i.e., not from any template).
        return rule_context.discourse_type == SharedDiscourseExtractor.NEW_VIS_NOT_FROM_EXISTING_TEMPLATE
