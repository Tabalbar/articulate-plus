from ..rule import Rule
from ..shared_discourse_extractor import SharedDiscourseExtractor
from ..shared_create_vis_from_existing_template_discourse_rules import Utilities

'''
- Step 4.2: process if the request is about creating a new vis from an existing template.

predicted data:
1. gesture reference distance in dialogue history (shared utility).
2. gesture referring expression (shared utility).
3. gesture target vis id (shared utility).
3. text reference distance in dialogue history (shared utility).
4. text referring expression (shared utility).
5. text target vis id (shared utility).
6. prev_spec.
7. prev_spec history.
8. merge prev spec to curr spec (shared).
9. curr spec gesture id (shared).
10. curr spec history (shared).
11. generate smarthub id.
12. add to dialogue history (shared).
'''


class SearchPreviousVisualizationSpecificationUsingGestureReferenceRule(Rule):
    def __init__(self):
        super().__init__()

    def execute(self, rule_context):
        # search dialogue history using gesture reference target vis id.
        #
        # additionally predict gesture reference distance in dialogue history.
        history_id = rule_context.context.gesture_target_vis_ids[-1]
        rule_context.prev_spec.cos_sim, \
            rule_context.request.pred_gesture_reference.dialogue_history_distance, \
            rule_context.prev_spec.spec = Utilities. \
            search_previous_visualization_specification_using_gesture_reference(rule_context=rule_context,
                                                                                history_id=history_id)

        if not rule_context.prev_spec.spec:
            return

        rule_context.request.pred_gesture_reference.target_vis_id = rule_context.prev_spec.spec.plot_headline.id
        rule_context.request.pred_gesture_reference.text = rule_context.request.pred_referring_expression.text

    def should_execute(self, rule_context):
        # check discourse type is creating new vis from existing template.
        #
        # check if co-occurring gesture reference exists.
        return rule_context.discourse_type == SharedDiscourseExtractor.NEW_VIS_FROM_EXISTING_TEMPLATE and \
               rule_context.context.gesture_target_vis_ids[-1] != -1 and \
               rule_context.request.pred_referring_expression.text is not None


class SearchPreviousVisualizationSpecificationUsingTextReferenceRule(Rule):
    def __init__(self):
        super().__init__()

    def execute(self, rule_context):
        # search dialogue history using text reference.
        #
        # additionally predict text reference distance in dialogue history.
        rule_context.prev_spec.cos_sim, rule_context.prev_spec.spec = Utilities.\
            search_previous_visualization_specification_using_text_reference(rule_context=rule_context)

        if not rule_context.prev_spec.spec:
            return

        rule_context.request.pred_text_reference.target_vis_id = rule_context.prev_spec.spec.plot_headline.id
        rule_context.request.pred_text_reference.text = rule_context.request.pred_referring_expression.text

        history_id = rule_context.request.pred_text_reference.target_vis_id
        rule_context.request.pred_text_reference.dialogue_history_distance = Utilities. \
            get_distance_to_previous_visualization_specification_using_text_reference(
                history_id=history_id,
                rule_context=rule_context)

    def should_execute(self, rule_context):
        # check discourse type is creating new vis from existing template.
        #
        # check if text reference exists.
        return rule_context.discourse_type == SharedDiscourseExtractor.NEW_VIS_FROM_EXISTING_TEMPLATE and \
               rule_context.request.pred_gesture_reference.target_vis_id == -1 and \
               rule_context.request.pred_referring_expression.text is not None


class VisualizationSpecificationStateUpdateRule(Rule):
    def __init__(self):
        super().__init__()

    def execute(self, rule_context):
        # assign latest available smarthub id to curr_spec id.
        rule_context.curr_spec.spec.plot_headline.id = rule_context.CURR_DIALOGUE_HISTORY.history_id

    def should_execute(self, rule_context):
        # check if discourse type is creating new vis from an existing template.
        # - note: either curr spec is the merged spec or the original curr spec at this point.
        # - so, no matter what, for new vis from existing template, we must add to dialogue history.
        # - hence, only need to check for discourse type is creating new vis from existing template.
        return rule_context.discourse_type == SharedDiscourseExtractor.NEW_VIS_FROM_EXISTING_TEMPLATE
