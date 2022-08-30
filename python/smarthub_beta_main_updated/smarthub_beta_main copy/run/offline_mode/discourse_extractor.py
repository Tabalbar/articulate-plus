"""
leverage the source vis id annotation (i.e., current vis id of focus during request) and target vis id annotation
(i.e. vis id being requested) to determine the discourse:

1. is_reference_to_vis_not_from_existing_template:
- reference to a vis (i.e., target vis id is not none) not based on existing template (i.e., source vis id is none).
- vis not already introduced to discourse.

2. is_reference_to_vis_from_existing_template:
- reference to a vis (i.e., target vis id is not none) based on existing template (i.e., source vis id is not none).
- target vis id not equal to source vis id.
- vis not already introduced to discourse.

3. existing_vis:
- vis already introduced to discourse.
"""
from ..shared_discourse_extractor import SharedDiscourseExtractor
from ..reference_extractor import ReferenceExtractor


class DiscourseExtractor(SharedDiscourseExtractor):

    def __init__(self, request, discourse_history):
        super().__init__(request=request)
        self.discourse_history = discourse_history

    def _load_vis_reference_component_info(self):
        reference_idx, _, self.source_vis_id, self.target_vis_id, _, _, _ = \
            ReferenceExtractor(self.request.vis_reference_component).extract_reference(which_one=0)

        self.reference = None
        if reference_idx != -1:
            self.reference = self.request.vis_reference_component[reference_idx]

    def is_reference_to_new_vis_not_from_existing_template(self):
        self._load_vis_reference_component_info()

        if not self.reference:
            return False

        if self.target_vis_id in self.discourse_history:
            return False

        return self.reference.get_sourcevis_ids_attribute() == 'none' and \
               self.reference.get_targetvis_ids_attribute() != 'none'

    def is_reference_to_new_vis_from_existing_template(self):
        self._load_vis_reference_component_info()

        if not self.reference:
            return False

        if self.target_vis_id in self.discourse_history:
            return False

        return self.reference.get_sourcevis_ids_attribute() != 'none' and \
               self.reference.get_targetvis_ids_attribute() != 'none' and \
               self.reference.get_sourcevis_ids_attribute() != self.reference.get_targetvis_ids_attribute()

    def is_reference_to_existing_vis(self):
        self._load_vis_reference_component_info()

        if not self.reference:
            return False

        if self.target_vis_id not in self.discourse_history:
            return False
        return True
