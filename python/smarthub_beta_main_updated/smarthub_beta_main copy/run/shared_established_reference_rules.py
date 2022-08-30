from app import VisualizationTaskConstructor, VisualizationSpecificationConstructor

'''
- Step 3: create a visualization specification for current request.
- do not add to dialogue history until discourse determination is made in subsequent steps.

1. curr_spec.
2. curr_spec gesture target id.
3. curr_spec history.
'''


class Utilities:
    @staticmethod
    def create_visualization_specification(rule_context, dialogue_act, referring_expression, gesture_target_vis_id):
        curr_task = VisualizationTaskConstructor.construct(
            rule_context.setup.utterances, rule_context.request.utterance, dialogue_act,
            referring_expression)

        curr_spec = VisualizationSpecificationConstructor.construct(curr_task, dialogue_act)
        curr_spec.plot_headline.id = rule_context.CURR_DIALOGUE_HISTORY.history_id
        curr_spec.gesture_target_id = gesture_target_vis_id
        _, curr_spec.plot_headline_history, _, _, _ = rule_context.CURR_DIALOGUE_HISTORY. \
            search_closest_cosine_similar_previous_visualization_specification(visualization_specification=curr_spec,
                                                                               minimum_similarity_cutoff=0.01,
                                                                               search_history_id_before=
                                                                               curr_spec.plot_headline.id)
        return curr_spec
