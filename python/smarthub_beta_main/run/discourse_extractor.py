"""
leverage the dialogue act to determine the discourse:

1. is_reference_to_vis_not_from_existing_template:
- dialogue act is 'createvis'.

2. is_reference_to_vis_from_existing_template:
- dialogue act is 'modifyvis'.

3. existing_vis:
- dialogue act is 'winmgmt'.
"""

from run.shared_discourse_extractor import SharedDiscourseExtractor


class DiscourseExtractor(SharedDiscourseExtractor):
    def __init__(self, request):
        super().__init__(request=request)

    def is_reference_to_new_vis_not_from_existing_template(self):
        return self.request.pred_dialogue_act[1] in ['createvis', 'preference', 'factbased', 'clarification']

    def is_reference_to_new_vis_from_existing_template(self):
        return self.request.pred_dialogue_act[1] == 'modifyvis'

    def is_reference_to_existing_vis(self):
        return self.request.pred_dialogue_act[1] == 'winmgmt'
