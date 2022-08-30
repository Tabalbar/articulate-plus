from ..shared_context import SharedContext
from .discourse_extractor import DiscourseExtractor


class RuleContext(SharedContext):
    CURR_DIALOGUE_HISTORY = None

    def __init__(self, context):
        super().__init__(context)
        self.discourse_extractor = DiscourseExtractor(request=self.request)

    def __str__(self):
        s = super().__str__()
        s += 'State- ' + str(self.CURR_DIALOGUE_HISTORY) + '\n'
        return s