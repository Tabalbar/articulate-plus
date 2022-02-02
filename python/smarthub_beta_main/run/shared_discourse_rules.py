from .shared_discourse_extractor import SharedDiscourseExtractor

'''
- Step 4: determine if the request is about creating a new vis (from scratch or template), or existing vis.

1. discourse type.
'''


class Utilities:
    @staticmethod
    def determine_discourse_type(rule_context):
        discourse_extractor = rule_context.discourse_extractor
        if discourse_extractor.is_reference_to_new_vis_not_from_existing_template():
            return SharedDiscourseExtractor.NEW_VIS_NOT_FROM_EXISTING_TEMPLATE
        elif discourse_extractor.is_reference_to_new_vis_from_existing_template():
            return SharedDiscourseExtractor.NEW_VIS_FROM_EXISTING_TEMPLATE
        elif discourse_extractor.is_reference_to_existing_vis():
            return SharedDiscourseExtractor.EXISTING_VIS
        return -1
