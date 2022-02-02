from ..rule import Rule
from ..shared_discourse_rules import Utilities

'''
- Step 4: determine if the request is about creating a new vis (from scratch or template), or existing vis.

gold data:
1. discourse type.
'''


class DiscourseTypeRule(Rule):
    def __init__(self):
        super().__init__()

    def execute(self, rule_context):
        # determine discourse type
        rule_context.discourse_type = Utilities.determine_discourse_type(rule_context)

    def should_execute(self, rule_context):
        # only vis reference annotation contains information about discourse type so check if it exists.
        return rule_context.request.vis_reference_component is not None
