import json

from .plot_headline import PlotHeadline


class VisualizationSpecification:
    def __init__(self):
        self.plot_headline = PlotHeadline()
        self.target_id = -1
        self.gesture_target_id = -1
        self.horizontal_axis = None
        self.horizontal_group_axis = None
        self.vertical_axis = None
        self.data_query = None
        self.data_query_results = []
        self.dialogue_act = None
        self.response_text = None
        self.visualization_task = None
        self.plot_headline_history = []

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
