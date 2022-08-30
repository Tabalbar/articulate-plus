from .rule import Rule
from .shared_discourse_extractor import SharedDiscourseExtractor

import itertools

'''
- Step 4.1: process if the request is about creating a new vis from scratch (i.e., not from any template).

1. established reference: curr_spec added to dialogue history (shared).
2. established reference: predict properties (shared).
'''


class VisualizationSpecificationDialogueHistoryAdditionRule(Rule):
    def __init__(self):
        super().__init__()

    def execute(self, rule_context):
        # add curr_spec to the dialogue history.
        rule_context.CURR_DIALOGUE_HISTORY.add_visualization_specification(rule_context.curr_spec.spec)

    def should_execute(self, rule_context):
        # discourse type is creating new vis from scratch (i.e., not from any template).
        return rule_context.discourse_type == SharedDiscourseExtractor.NEW_VIS_NOT_FROM_EXISTING_TEMPLATE


class PredictVisualizationSpecificationPropertiesRule(Rule):
    def __init__(self):
        super().__init__()

    def execute(self, rule_context):
        rule_context.request.pred_properties = list(itertools.chain(*[[item.lower() for item in value] for value
            in rule_context.curr_spec.spec.visualization_task.filters.values()]))

        if rule_context.prev_spec.spec:
            rule_context.request.pred_properties += list(itertools.chain(*[[item.lower() for item in value] for value
                in rule_context.curr_spec.spec.visualization_task.filters.values()]))

        rule_context.request.pred_properties += [aggregator.lower() for aggregator, entity_value in
                                                 rule_context.curr_spec.spec.visualization_task.aggregators]
        rule_context.request.pred_properties += [entity.text.lower() for entity in
                                                 rule_context.request.utterance._.entities]
        rule_context.request.pred_properties = sorted(list(set(rule_context.request.pred_properties)))

    def should_execute(self, rule_context):
        # check if discourse type is creating new vis from scratch (i.e., not from any template).
        return rule_context.discourse_type == SharedDiscourseExtractor.NEW_VIS_NOT_FROM_EXISTING_TEMPLATE