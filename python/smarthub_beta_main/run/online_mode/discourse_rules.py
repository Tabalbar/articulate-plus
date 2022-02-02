from ..rule import Rule
from ..shared_discourse_rules import Utilities

'''
- Step 4: determine if the request is about creating a new vis (from scratch or template), or existing vis.

predicted data:
1. discourse type.
'''


class DiscourseTypeRule(Rule):
    def __init__(self):
        super().__init__()

    def execute(self, rule_context):
        rule_context.discourse_type = Utilities.determine_discourse_type(rule_context)

    def should_execute(self, rule_context):
        # as long as predicted dialogue act exists (which it always does so no need to check), then
        # can determine discourse type.
        return True
