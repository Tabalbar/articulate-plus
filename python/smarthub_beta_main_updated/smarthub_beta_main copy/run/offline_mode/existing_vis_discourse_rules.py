from .statistics_util import StatisticsUtil
from ..rule import Rule
from ..shared_discourse_extractor import SharedDiscourseExtractor
from ..shared_existing_vis_discourse_rules import Utilities
from .statistics import Statistics

'''
- Step 4.3: process if the request is about an existing vis.

gold data:
1. gesture reference distance in dialogue history.
2. text reference distance in dialogue history.

predicted data:
1. gesture reference distance in dialogue history (shared utility).
2. gesture referring expression.
3. gesture target vis id.
3. text reference distance in dialogue history (shared utility).
4. text referring expression.
5. text target vis id.
6. referring expression.
7. referring expression target vis id.
8. prev_spec.
9. prev_spec history.
10. merge prev spec to curr spec (shared).
11. curr spec target id (shared).
12. curr spec history (shared).
13. remove prev spec from dialogue history (if "close" request) (shared).

statistics:
1. compare gold gesture reference distance in dialogue history to 
   predicted gesture reference distance in dialogue history.
2. compare gold text reference distance in dialogue history to 
   predicted text reference distance in dialogue history.
3. compare gold gesture target vis id to predicted gesture target vis id.
4. compare gold text target vis id to predicted text target vis id.
5. compare gold gesture referring expression to predicted gesture referring expression.
6. compare gold text referring expression to predicted text referring expression.
'''


class ExtractDistanceToPreviousVisualizationUsingGestureReferenceRule(Rule):
    def __init__(self):
        super().__init__()

    def execute(self, rule_context):
        # extract gold gesture reference distance in dialogue history.
        history_id = rule_context.CURR_VIS_ID_TO_HISTORY_ID[rule_context.request.gold_gesture_reference.target_vis_id]
        rule_context.request.gold_gesture_reference.dialogue_history_distance, _ = \
            rule_context.CURR_DIALOGUE_HISTORY.search_visualization_specification_by_history_id(
                target_history_id=history_id, search_history_id_before=rule_context.curr_spec.spec.plot_headline.id)

    def should_execute(self, rule_context):
        # check discourse type is existing vis.
        #
        # check if co-occurring gesture reference exists.
        #
        # if gold gesture target vis id does not match to any spec in dialogue history:
        # - not a valid gesture reference so do not attempt prediction.
        return rule_context.discourse_type == SharedDiscourseExtractor.EXISTING_VIS and \
               rule_context.request.gold_gesture_reference.target_vis_id != -1 and \
               rule_context.request.gold_gesture_reference.text is not None and \
               rule_context.request.gold_gesture_reference.target_vis_id in rule_context.CURR_VIS_ID_TO_HISTORY_ID


class SearchPreviousVisualizationSpecificationUsingGestureReferenceRule(Rule):
    def __init__(self):
        super().__init__()

    def execute(self, rule_context):
        # search dialogue history using gesture reference target vis id.
        #
        # additionally predict gesture reference distance in dialogue history.
        history_id = rule_context.CURR_VIS_ID_TO_HISTORY_ID[rule_context.request.gold_gesture_reference.target_vis_id]
        rule_context.prev_spec.cos_sim, \
            rule_context.request.pred_gesture_reference.dialogue_history_distance, \
            rule_context.prev_spec.spec = Utilities. \
            search_previous_visualization_specification_using_gesture_reference(rule_context=rule_context,
                                                                                history_id=history_id)
        if not rule_context.prev_spec.spec:
            return

        rule_context.request.pred_gesture_reference.target_vis_id = rule_context.CURR_HISTORY_ID_TO_VIS_ID[
            rule_context.prev_spec.spec.plot_headline.id]
        rule_context.request.pred_referring_expression.target_vis_id = \
            rule_context.request.pred_gesture_reference.target_vis_id
        rule_context.request.pred_gesture_reference.text = rule_context.request.pred_referring_expression.text

    def should_execute(self, rule_context):
        # check discourse type is existing vis.
        #
        # check if co-occurring gesture reference exists.
        #
        # if gold gesture target vis id does not match to any spec in dialogue history:
        # - not a valid gesture reference so do not attempt prediction.
        return rule_context.discourse_type == SharedDiscourseExtractor.EXISTING_VIS and \
               rule_context.request.gold_gesture_reference.target_vis_id != -1 and \
               rule_context.request.gold_gesture_reference.text is not None and \
               rule_context.request.gold_gesture_reference.target_vis_id in rule_context.CURR_VIS_ID_TO_HISTORY_ID


class GestureTargetIdStatisticsRule(Rule):
    def __init__(self):
        super().__init__()

    def execute(self, rule_context):
        distribution = Statistics.gesture_reference_target_vis_ids_match_distribution.distributions[-1]

        distribution.total_labels += 1

        if rule_context.request.pred_gesture_reference.target_vis_id != -1:
            if rule_context.request.gold_gesture_reference.target_vis_id == \
                    rule_context.request.pred_gesture_reference.target_vis_id:
                distribution.total_labels_matched += 1

    def should_execute(self, rule_context):
        return rule_context.discourse_type == SharedDiscourseExtractor.EXISTING_VIS and \
               rule_context.request.gold_gesture_reference.target_vis_id != -1 and \
               rule_context.request.gold_gesture_reference.text is not None and \
               rule_context.request.gold_gesture_reference.target_vis_id in rule_context.CURR_VIS_ID_TO_HISTORY_ID


class GestureReferringExpressionStatisticsRule(Rule):
    def __init__(self):
        super().__init__()

    def execute(self, rule_context):
        distribution = Statistics.gesture_reference_texts_match_distribution.distributions[-1]

        distribution.total_labels += 1

        if rule_context.request.pred_gesture_reference.text:
            distribution.total_labels_matched += 1

    def should_execute(self, rule_context):
        return rule_context.discourse_type == SharedDiscourseExtractor.EXISTING_VIS and \
               rule_context.request.gold_gesture_reference.target_vis_id != -1 and \
               rule_context.request.gold_gesture_reference.text is not None and \
               rule_context.request.gold_gesture_reference.target_vis_id in rule_context.CURR_VIS_ID_TO_HISTORY_ID


class GestureTargetIdDistanceStatisticsRule(Rule):
    def __init__(self):
        super().__init__()

    def execute(self, rule_context):
        distribution = Statistics.gesture_reference_distance_frequency_distribution.distributions[-1]
        distribution.gold_label_frequencies[rule_context.request.gold_gesture_reference.dialogue_history_distance] += 1
        distribution.pred_label_frequencies[rule_context.request.pred_gesture_reference.dialogue_history_distance] += 1

    def should_execute(self, rule_context):
        return rule_context.discourse_type == SharedDiscourseExtractor.EXISTING_VIS and \
               rule_context.request.gold_gesture_reference.target_vis_id != -1 and \
               rule_context.request.gold_gesture_reference.text is not None and \
               rule_context.request.gold_gesture_reference.target_vis_id in rule_context.CURR_VIS_ID_TO_HISTORY_ID


class ExtractDistanceToPreviousVisualizationUsingTextReferenceRule(Rule):
    def __init__(self):
        super().__init__()

    def execute(self, rule_context):
        # extract gold text reference distance in dialogue history.
        history_id = rule_context.CURR_VIS_ID_TO_HISTORY_ID[rule_context.request.gold_text_reference.target_vis_id]
        rule_context.request.gold_text_reference.dialogue_history_distance, _ = \
            rule_context.CURR_DIALOGUE_HISTORY.search_visualization_specification_by_history_id(
                target_history_id=history_id, search_history_id_before=rule_context.curr_spec.spec.plot_headline.id)

    def should_execute(self, rule_context):
        # check discourse type is existing vis.
        #
        # check if text reference exists.
        #
        # if gold text target vis id does not match to any spec in dialogue history:
        # - not a valid text reference so do not attempt prediction.
        return rule_context.discourse_type == SharedDiscourseExtractor.EXISTING_VIS and \
               rule_context.request.gold_text_reference.target_vis_id != -1 and \
               rule_context.request.gold_text_reference.text is not None and \
               rule_context.request.gold_text_reference.target_vis_id in rule_context.CURR_VIS_ID_TO_HISTORY_ID


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

        rule_context.request.pred_text_reference.target_vis_id = rule_context.CURR_HISTORY_ID_TO_VIS_ID[
            rule_context.prev_spec.spec.plot_headline.id]
        rule_context.request.pred_referring_expression.target_vis_id = \
            rule_context.request.pred_text_reference.target_vis_id
        rule_context.request.pred_text_reference.text = rule_context.request.pred_referring_expression.text

        history_id = rule_context.CURR_VIS_ID_TO_HISTORY_ID[rule_context.request.pred_text_reference.target_vis_id]
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
               rule_context.request.gold_text_reference.target_vis_id != -1 and \
               rule_context.request.gold_text_reference.text is not None and \
               rule_context.request.gold_text_reference.target_vis_id in rule_context.CURR_VIS_ID_TO_HISTORY_ID


class TextTargetIdStatisticsRule(Rule):
    def __init__(self):
        super().__init__()

    def execute(self, rule_context):
        distribution = Statistics.text_reference_target_vis_ids_match_distribution.distributions[-1]

        distribution.total_labels += 1

        if rule_context.request.pred_text_reference.target_vis_id != -1 and \
                rule_context.request.gold_text_reference.target_vis_id == \
                rule_context.request.pred_text_reference.target_vis_id:
            distribution.total_labels_matched += 1

    def should_execute(self, rule_context):
        # if target vis id == -1 it means no valid target vis id was found.
        # - possible since in earlier conversation, user may have referred to multiple vis and none are valid.
        # - possible since reference may not exist (i.e., target vis id initialized to -1).

        return rule_context.discourse_type == SharedDiscourseExtractor.EXISTING_VIS and \
               rule_context.request.gold_text_reference.target_vis_id != -1 and \
               rule_context.request.gold_text_reference.text is not None and \
               rule_context.request.gold_text_reference.target_vis_id in rule_context.CURR_VIS_ID_TO_HISTORY_ID


class TextReferringExpressionStatisticsRule(Rule):
    def __init__(self):
        super().__init__()

    def execute(self, rule_context):
        distribution = Statistics.text_reference_texts_match_distribution.distributions[-1]

        distribution.total_labels += 1

        if rule_context.request.pred_text_reference.text:
            distribution.total_labels_matched += 1

    def should_execute(self, rule_context):
        return rule_context.discourse_type == SharedDiscourseExtractor.EXISTING_VIS and \
               rule_context.request.gold_text_reference.target_vis_id != -1 and \
               rule_context.request.gold_text_reference.text is not None and \
               rule_context.request.gold_text_reference.target_vis_id in rule_context.CURR_VIS_ID_TO_HISTORY_ID


class TextTargetIdDistanceStatisticsRule(Rule):
    def __init__(self):
        super().__init__()

    def execute(self, rule_context):
        distribution = Statistics.text_reference_distance_frequency_distribution.distributions[-1]
        distribution.gold_label_frequencies[rule_context.request.gold_text_reference.dialogue_history_distance] += 1
        distribution.pred_label_frequencies[rule_context.request.pred_text_reference.dialogue_history_distance] += 1

    def should_execute(self, rule_context):
        return rule_context.discourse_type == SharedDiscourseExtractor.EXISTING_VIS and \
               rule_context.request.gold_text_reference.target_vis_id != -1 and \
               rule_context.request.gold_text_reference.text is not None and \
               rule_context.request.gold_text_reference.target_vis_id in rule_context.CURR_VIS_ID_TO_HISTORY_ID


class MergePreviousVisualizationSpecificationAndCurrentVisualizationSpecificationRule(Rule):
    def __init__(self):
        super().__init__()

    def execute(self, rule_context):
        # merge prev spec to curr spec.
        merged_spec = Utilities.merge_previous_visualization_specification_and_current_visualization_specification(
            rule_context=rule_context)

        # commented out since performing close would impact total statistical numbers for different window search sizes.
        '''if merged_spec.visualization_task.action == 'close':
            rule_context.CURR_DIALOGUE_HISTORY.remove_visualization_specification(rule_context.prev_spec.spec)

            history_id = rule_context.prev_spec.spec.plot_headline.id
            vis_id = rule_context.CURR_HISTORY_ID_TO_VIS_ID[history_id]

            rule_context.CURR_HISTORY_ID_TO_VIS_ID.pop(history_id)
            rule_context.CURR_VIS_ID_TO_HISTORY_ID.pop(vis_id)'''

        rule_context.curr_spec.spec = merged_spec

    def should_execute(self, rule_context):
        # check discourse type is existing vis.
        #
        # check that prev_spec was found from earlier search of dialogue history.
        return rule_context.discourse_type == SharedDiscourseExtractor.EXISTING_VIS and \
               rule_context.prev_spec.spec is not None
