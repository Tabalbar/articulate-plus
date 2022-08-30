from .reference_target import ReferenceTarget


class RequestData:
    def __init__(self):
        self.component = None

        self.utterance_id = -1
        self.utterance = None

        self.utterance_component = None
        self.gesture_reference_component = None
        self.text_reference_component = None
        self.vis_reference_component = None

        self.gold_dialogue_act = None
        self.pred_dialogue_act = None

        self.gold_referring_expression = ReferenceTarget()
        self.pred_referring_expression = ReferenceTarget()

        self.gold_gesture_reference = ReferenceTarget()
        self.pred_gesture_reference = ReferenceTarget()

        self.gold_text_reference = ReferenceTarget()
        self.pred_text_reference = ReferenceTarget()

        self.gold_properties = []
        self.pred_properties = []
