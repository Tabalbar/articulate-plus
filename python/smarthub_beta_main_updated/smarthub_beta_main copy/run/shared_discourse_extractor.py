from abc import ABCMeta, abstractmethod


class SharedDiscourseExtractor:
    __metaclass__ = ABCMeta

    EXISTING_VIS = 0
    NEW_VIS_FROM_EXISTING_TEMPLATE = 1
    NEW_VIS_NOT_FROM_EXISTING_TEMPLATE = 2

    def __init__(self, request):
        self.request = request

    def extract(self):
        if self.is_reference_to_new_vis_not_from_existing_template():
            return SharedDiscourseExtractor.NEW_VIS_NOT_FROM_EXISTING_TEMPLATE

        elif self.is_reference_to_new_vis_from_existing_template():
            return SharedDiscourseExtractor.NEW_VIS_FROM_EXISTING_TEMPLATE

        elif self.is_reference_to_existing_vis():
            return SharedDiscourseExtractor.EXISTING_VIS

        return -1

    @abstractmethod
    def is_reference_to_new_vis_not_from_existing_template(self):
        raise NotImplementedError()

    @abstractmethod
    def is_reference_to_new_vis_from_existing_template(self):
        raise NotImplementedError()

    def is_reference_to_new_vis(self):
        return self.is_reference_to_new_vis_not_from_existing_template() or \
               self.is_reference_to_new_vis_from_existing_template()

    def is_reference_to_existing_vis(self):
        raise NotImplementedError()
