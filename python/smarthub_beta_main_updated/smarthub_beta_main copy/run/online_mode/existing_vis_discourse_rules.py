from ..rule import Rule
from ..shared_discourse_extractor import SharedDiscourseExtractor
from ..shared_existing_vis_discourse_rules import Utilities

'''
- Step 4.3: process if the request is about existing vis.

predicted data:
1. gesture reference distance in dialogue history (shared utility).
2. gesture referring expression.
3. gesture target vis id.
3. text reference distance in dialogue history (shared utility).
4. text referring expression.
5. text target vis id
6. referring expression.
7. referring expression target vis id.
8. prev_spec.
9. prev_spec history.
10. merge prev spec to curr spec (shared).
11. curr spec target id (shared).
12. curr spec history (shared).
13. remove prev spec from dialogue history (if "close" request) (shared).
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
        rule_context.prev_spec.spec = \
                Utilities.search_previous_visualization_specification_using_gesture_reference(
                    rule_context=rule_context,
                    history_id=history_id)

        if not rule_context.prev_spec.spec:
            return

        rule_context.request.pred_gesture_reference.target_vis_id = rule_context.prev_spec.spec.plot_headline.id
        rule_context.request.pred_gesture_reference.text = rule_context.request.pred_referring_expression.text

    def should_execute(self, rule_context):
        # check discourse type is existing vis.
        #
        # check if co-occurring gesture reference exists.
        #
        # if gold gesture target vis id does not match to any spec in dialogue history:
        # - not a valid gesture reference so do not attempt prediction.
        return rule_context.discourse_type == SharedDiscourseExtractor.NEW_VIS_FROM_EXISTING_TEMPLATE and \
               rule_context.context.gesture_target_vis_ids[-1] != -1 and \
               (rule_context.request.pred_referring_expression.text is not None or
                rule_context.curr_spec.spec.visualization_task.action is not None)


class SearchPreviousVisualizationSpecificationUsingTextReferenceRule(Rule):
    def __init__(self):
        super().__init__()

    def execute(self, rule_context):
        # search dialogue history using text reference.
        #
        # additionally predict text reference distance in dialogue history.
        rule_context.prev_spec.cos_sim, rule_context.prev_spec.spec = \
            Utilities.search_previous_visualization_specification_using_text_reference(rule_context=rule_context)

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
        # check discourse type is existing vis.
        #
        # check if text reference exists.
        #
        # if gold text target vis id does not match to any spec in dialogue history:
        # - not a valid text reference so do not attempt prediction.
        return rule_context.discourse_type == SharedDiscourseExtractor.EXISTING_VIS and \
               rule_context.context.gesture_target_vis_ids[-1] == -1 and \
               (rule_context.request.pred_referring_expression.text is not None or
                rule_context.curr_spec.spec.visualization_task.action is not None)


class MergePreviousVisualizationSpecificationAndCurrentVisualizationSpecificationRule(Rule):
    def __init__(self):
        super().__init__()

    def execute(self, rule_context):
        merged_spec = Utilities.merge_previous_visualization_specification_and_current_visualization_specification(
            rule_context=rule_context)

        if merged_spec.visualization_task.action == 'close':
            rule_context.CURR_DIALOGUE_HISTORY.remove_visualization_specification(rule_context.prev_spec.spec)

        rule_context.curr_spec.spec = merged_spec

    def should_execute(self, rule_context):
        # check discourse type is existing vis.
        #
        # check that prev_spec was found from earlier search of dialogue history.
        return rule_context.discourse_type == SharedDiscourseExtractor.EXISTING_VIS and \
               rule_context.prev_spec.spec is not None
