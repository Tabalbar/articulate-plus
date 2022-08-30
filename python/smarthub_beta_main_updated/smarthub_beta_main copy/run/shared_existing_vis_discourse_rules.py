from .shared_discourse_extractor import SharedDiscourseExtractor
from .rule import Rule
from app import StateUtils

from scipy.spatial.distance import cosine
'''
- Step 4.3: process if the request is about an existing vis.

1. merge prev spec to curr spec (shared).
2. curr spec target id (shared).
3. curr spec history (shared).
4. remove prev spec from dialogue history (if "close" request) (shared).
'''


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

        _, rule_context.prev_spec.plot_headline_history, _, _, _ = rule_context.CURR_DIALOGUE_HISTORY. \
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
                minimum_similarity_cutoff=0.10,
                search_history_id_before=rule_context.curr_spec.spec.plot_headline.id)

        if not prev_spec:
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

        return cos_sim[idx], prev_spec

    @staticmethod
    def get_distance_to_previous_visualization_specification_using_text_reference(history_id, rule_context):
        dialogue_history_distance, _ = \
            rule_context.CURR_DIALOGUE_HISTORY.search_visualization_specification_by_history_id(
                target_history_id=history_id, search_history_id_before=rule_context.curr_spec.spec.plot_headline.id)

        return dialogue_history_distance

    @staticmethod
    def merge_previous_visualization_specification_and_current_visualization_specification(rule_context):

        merged_spec = rule_context.curr_spec.spec
        history_id = rule_context.prev_spec.spec.plot_headline.id

        merged_spec.target_id = history_id

        merged_spec.plot_headline_history = rule_context.curr_spec.spec.plot_headline_history

        return merged_spec
