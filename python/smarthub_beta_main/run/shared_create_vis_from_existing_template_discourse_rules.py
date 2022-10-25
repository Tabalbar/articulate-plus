from app import VisualizationTaskConstructor, VisualizationSpecificationConstructor
from .shared_discourse_extractor import SharedDiscourseExtractor
from .rule import Rule
from app import StateUtils

from scipy.spatial.distance import cosine
import itertools

'''
- Step 4.2: process if the request is about creating a new vis from an existing template.

1. merge prev spec to curr spec (shared).
2. curr spec gesture id (shared).
3. curr spec history (shared).
4. add to dialogue history (shared).
5. gesture reference distance in dialogue history (shared utility).
6. text reference distance in dialogue history (shared utility).
'''


class MergePreviousVisualizationSpecificationAndCurrentVisualizationSpecificationRule(Rule):
    def __init__(self):
        super().__init__()

    def execute(self, rule_context):
        # merge prev spec to curr spec.
        curr_task = rule_context.curr_spec.spec.visualization_task
        prev_task = rule_context.prev_spec.spec.visualization_task

        merged_task = VisualizationTaskConstructor.merge_construct(prev_task, curr_task)

        merged_spec = VisualizationSpecificationConstructor.construct(merged_task, rule_context.request.
                                                                      pred_dialogue_act)
        merged_spec.gesture_target_id = rule_context.curr_spec.spec.gesture_target_id
        merged_spec.target_id = rule_context.prev_spec.spec.plot_headline.id
        rule_context.curr_spec.spec.plot_headline.summary = merged_task.summary
        merged_spec.plot_headline = rule_context.curr_spec.spec.plot_headline

        merged_spec.plot_headline_history = rule_context.curr_spec.spec.plot_headline_history

        rule_context.curr_spec.spec = merged_spec

    def should_execute(self, rule_context):
        # check discourse type is creating new vis from existing template.
        #
        # check that prev_spec was found from earlier search of dialogue history.
        return rule_context.discourse_type == SharedDiscourseExtractor.NEW_VIS_FROM_EXISTING_TEMPLATE and \
               rule_context.prev_spec.spec is not None


class VisualizationSpecificationDialogueHistoryAdditionRule(Rule):
    def __init__(self):
        super().__init__()

    def execute(self, rule_context):
        # add curr_spec to the dialogue history.
        rule_context.CURR_DIALOGUE_HISTORY.add_visualization_specification(rule_context.curr_spec.spec)

    def should_execute(self, rule_context):
        # check discourse type is creating new vis from existing template.
        # - note: either curr spec is the merged spec or the original curr spec at this point.
        # - so, no matter what, for new vis from existing template, we must add to dialogue history.
        # - hence, only need to check for discourse type is creating new vis from existing template.
        return rule_context.discourse_type == SharedDiscourseExtractor.NEW_VIS_FROM_EXISTING_TEMPLATE


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
        return rule_context.discourse_type == SharedDiscourseExtractor.NEW_VIS_FROM_EXISTING_TEMPLATE


class Utilities:
    @staticmethod
    def search_previous_visualization_specification_using_gesture_reference(history_id, rule_context):
        dialogue_history_distance, \
            prev_spec = \
            rule_context.CURR_DIALOGUE_HISTORY.search_visualization_specification_by_history_id(
                target_history_id=history_id, search_history_id_before=rule_context.curr_spec.spec.plot_headline.id)

        if not prev_spec:
            return 0.0, dialogue_history_distance, None

        prev_feature_vector = StateUtils.transform_to_feature_vector(visualization_specification=prev_spec)
        curr_feature_vector = StateUtils.transform_to_feature_vector(visualization_specification=
                                                                     rule_context.curr_spec.spec)
        cos_sim = 1 - cosine(prev_feature_vector.reshape(1, -1), curr_feature_vector.reshape(1, -1))

        _, prev_spec.plot_headline_history, _, _, _ = rule_context.CURR_DIALOGUE_HISTORY. \
            search_closest_cosine_similar_previous_visualization_specification(
                visualization_specification=prev_spec,
                search_history_id_before=prev_spec.plot_headline.id + 1,
                minimum_similarity_cutoff=0.01)

        return cos_sim, dialogue_history_distance, prev_spec

    @staticmethod
    def search_previous_visualization_specification_using_text_reference(rule_context):
        _, \
            _, \
            cos_sim, \
            prev_spec, \
            idx = rule_context.CURR_DIALOGUE_HISTORY. \
            search_closest_cosine_similar_previous_visualization_specification(
                visualization_specification=rule_context.curr_spec.spec,
                minimum_similarity_cutoff=0.40,
                search_history_id_before=rule_context.curr_spec.spec.plot_headline.id)
        

        if not prev_spec:
            print("if not prev_spec")
            _, prev_spec = rule_context.CURR_DIALOGUE_HISTORY.search_visualization_specification_by_history_id(
                target_history_id=-1)

        if not prev_spec:
            return 0.0, None

        if not idx:
            prev_feature_vector = StateUtils.transform_to_feature_vector(visualization_specification=prev_spec)
            curr_feature_vector = StateUtils.transform_to_feature_vector(visualization_specification=
                                                                         rule_context.curr_spec.spec)
            cos_sim = [1-cosine(prev_feature_vector.reshape(1, -1), curr_feature_vector.reshape(1, -1))]
            idx = 0

        _, prev_spec.plot_headline_history, _, _, _ = rule_context.CURR_DIALOGUE_HISTORY. \
            search_closest_cosine_similar_previous_visualization_specification(
                visualization_specification=prev_spec,
                minimum_similarity_cutoff=0.01,
                search_history_id_before=prev_spec.plot_headline.id + 1)

        print("cos sim "+ str(cos_sim[idx]))
        with open('python_log.txt', 'a', encoding='utf-8') as log_file:
            log_file.write("\ncos sim :" + str(cos_sim[idx]))
            log_file.write("\n")
        
        return cos_sim[idx], prev_spec

    @staticmethod
    def get_distance_to_previous_visualization_specification_using_text_reference(history_id, rule_context):
        dialogue_history_distance, _ = \
            rule_context.CURR_DIALOGUE_HISTORY.search_visualization_specification_by_history_id(
                target_history_id=history_id, search_history_id_before=rule_context.curr_spec.spec.plot_headline.id)
        print("Distance to previous visualization specification :"+ str(dialogue_history_distance))
        with open('python_log.txt', 'a', encoding='utf-8') as log_file:
            log_file.write("\nDistance to previous visualization specification :"+ str(dialogue_history_distance))
            log_file.write("\n")

        return dialogue_history_distance