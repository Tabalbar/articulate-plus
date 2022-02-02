from run.setup_data import SetupData
from run.request_data import RequestData
from run.spec_search_data import SpecSearchData

from abc import ABCMeta

import json


class SharedContext:
    __metaclass__ = ABCMeta

    def __init__(self, context):
        self.curr_spec = SpecSearchData()
        self.prev_spec = SpecSearchData()

        self.context = context
        self.setup = SetupData()
        self.request = RequestData()

        self.discourse_type = -1

    def __str__(self):
        s = ''
        s += 'UTT - ' + self.request.utterance.text + '\n'
        s += 'UTTID - ' + str(self.request.utterance_id) + '\n'
        s += 'DA Gold- ' + str(self.request.gold_dialogue_act) + '\n'
        s += 'DA Pred- ' + str(self.request.pred_dialogue_act) + '\n'

        s += 'RE Pred- ' + str((self.request.pred_referring_expression.text,
                                self.request.pred_referring_expression.target_vis_id)) + '\n'

        s += 'Gesture Targetid Pred- ' + str(self.request.pred_gesture_reference.target_vis_id) + '\n'
        s += 'Gesture Targetid Gold- ' + str(self.request.gold_gesture_reference.target_vis_id) + '\n'

        s += 'Gesture Text Pred- ' + str(self.request.pred_gesture_reference.text) + '\n'
        s += 'Gesture Text Gold- ' + str(self.request.gold_gesture_reference.text) + '\n'

        s += 'Text Targetid Pred- ' + str(self.request.pred_text_reference.target_vis_id) + '\n'
        s += 'Text Targetid Gold- ' + str(self.request.gold_text_reference.target_vis_id) + '\n'

        s += 'Text Text Pred- ' + str(self.request.pred_text_reference.text) + '\n'
        s += 'Text Text Gold- ' + str(self.request.gold_text_reference.text) + '\n'

        s += 'Properties Pred- ' + str(self.request.pred_properties) + '\n'
        s += 'Properties Gold- ' + str(self.request.gold_properties) + '\n'

        s += 'Discourse Type- ' + str(self.discourse_type) + '\n'

        return s

    def get_json_obj(self):
        s = json.dumps(self, default=self._to_json, sort_keys=True, indent=4)
        obj = json.loads(s)
        return obj

    def get_json_str(self):
        return json.dumps(self, default=self._to_json, sort_keys=True, indent=4)

    def _to_json(self, o):
        if hasattr(o, '__dict__'):
            return o.__dict__
        elif isinstance(o, set):
            return list(o)