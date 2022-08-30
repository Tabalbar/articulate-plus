from ..rule import Rule
from .discourse_extractor import ReferenceExtractor
from run.offline_mode.statistics import Statistics

'''
- Step 1: process the input to the system.
- target vis id is maintained by visualization executor.
- history id (i.e., smarthub id) is maintained by smarthub.
- the annotated (i.e., gold) gesture target vis id is used 
  as predicted gesture target vis id.

gold data:
1. setup utterances.
2. request utterances.
3. referring expression
4. referring expression target vis id.
5. gesture target vis id.
6. gesture referring expression.
7. text target vis id.
8. text referring expression.
'''


class ContextComponentExtractionRule(Rule):
    def __init__(self):
        super().__init__()

    def execute(self, rule_context):
        # extract the setup and request components.
        rule_context.setup.component, rule_context.request.component, _ = rule_context.context.get_context()

    def should_execute(self, rule_context):
        return True


class SetupExtractionRule(Rule):
    def __init__(self):
        super().__init__()

    def execute(self, rule_context):
        # extract the setup utterances and their corresponding utterance ids.
        for component in rule_context.setup.component:
            utterance_component, _, _, _, _ = \
                component.get_context_component()

            utterance_id = utterance_component.get_utteranceid_attribute()
            utterance = utterance_component.get_utterance_attribute()

            rule_context.setup.utterances.append(rule_context.ENTITY_TOKENIZER(utterance))
            rule_context.setup.utterance_ids.append(utterance_id)

    def should_execute(self, rule_context):
        return True


class RequestExtractionRule(Rule):
    def __init__(self):
        super().__init__()

    def execute(self, rule_context):
        # extract the request utterance and corresponding utterance id.
        rule_context.request.utterance_component, _, rule_context.request.gesture_reference_component, \
            rule_context.request.text_reference_component, rule_context.request.vis_reference_component = \
            rule_context.request.component.get_context_component()

        rule_context.request.utterance_id = rule_context.request.utterance_component.get_utteranceid_attribute()
        rule_context.request.utterance = rule_context.ENTITY_TOKENIZER(
            rule_context.request.utterance_component.get_utterance_attribute())

    def should_execute(self, rule_context):
        return True


class GestureExtractionRule(Rule):
    def __init__(self):
        super().__init__()

    def execute(self, rule_context):
        # extract the gold gesture references (gesture target vis id + gesture referring expression).
        _, referring_expression_words_infos, _, target_vis_id, _, referring_expression_infos, _ = \
            ReferenceExtractor(rule_context.request.gesture_reference_component).extract_reference(which_one=-1)

        if not referring_expression_infos:
            return

        rule_context.request.gold_gesture_reference.referring_expression_info = referring_expression_infos[0]
        rule_context.request.gold_referring_expression.text = referring_expression_words_infos[0]
        rule_context.request.gold_referring_expression.target_vis_id = target_vis_id

        rule_context.request.gold_gesture_reference.text = referring_expression_words_infos[0]
        rule_context.request.gold_gesture_reference.target_vis_id = target_vis_id

    def should_execute(self, rule_context):
        # the reference exists.
        return rule_context.request.gesture_reference_component is not None and \
            rule_context.request.gesture_reference_component[0].get_referringexpression_attribute() is not None and \
                len(rule_context.request.gesture_reference_component[0].get_referringexpression_attribute()) > 0


class TextExtractionRule(Rule):
    def __init__(self):
        super().__init__()

    def execute(self, rule_context):
        # extract the gold text references (text target vis id + text referring expression).
        _, referring_expression_words_infos, _, target_vis_id, _, referring_expression_infos, _ = \
            ReferenceExtractor(rule_context.request.text_reference_component).extract_reference(which_one=-1)

        if not referring_expression_infos:
            return

        rule_context.request.gold_referring_expression.referring_expression_info = referring_expression_infos[0]
        rule_context.request.gold_referring_expression.text = referring_expression_words_infos[0]
        rule_context.request.gold_referring_expression.target_vis_id = target_vis_id

        rule_context.request.gold_text_reference.text = referring_expression_words_infos[0]
        rule_context.request.gold_text_reference.target_vis_id = target_vis_id

    def should_execute(self, rule_context):
        # the reference exists.
        return rule_context.request.text_reference_component is not None and \
            rule_context.request.text_reference_component[0].get_referringexpression_attribute() is not None and \
                len(rule_context.request.text_reference_component[0].get_referringexpression_attribute()) > 0
