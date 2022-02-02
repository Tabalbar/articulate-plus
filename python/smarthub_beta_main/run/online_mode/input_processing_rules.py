from ..rule import Rule

'''
- Step 1: process the input to the system.
- no difference between target vis id and history id,  (i.e., smarthub id) is maintained by smarthub.

predicted data:
1. setup utterances.
2. request utterances.
'''


class SetupExtractionRule(Rule):
    def __init__(self):
        super().__init__()

    def execute(self, rule_context):
        # extract the setup utterances and their corresponding utterance ids.
        for setup_utterance in rule_context.context.utterances[:-1]:
            rule_context.setup.utterances.append(setup_utterance)

    def should_execute(self, rule_context):
        return True


class RequestExtractionRule(Rule):
    def __init__(self):
        super().__init__()

    def execute(self, rule_context):
        # extract the request utterance and corresponding utterance id.
        rule_context.request.utterance = rule_context.context.utterances[-1]

    def should_execute(self, rule_context):
        return True
