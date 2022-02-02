from ..shared_context import SharedContext
from .discourse_extractor import DiscourseExtractor
from model_paths import ModelPaths
from dev.data_extractor.data_extraction_paths import DataExtractionPaths
from dev.data_extractor.entitiesextractor import EntitiesExtractor


class RuleContext(SharedContext):
    CURR_VIS_ID_TO_HISTORY_ID = None
    CURR_HISTORY_ID_TO_VIS_ID = None
    CURR_DIALOGUE_HISTORY = None
    ENTITY_TOKENIZER = None
    FOLD = 0
    USE_FULL_CONTEXT_WINDOW_FOR_DA_PREDICTION = True

    KNOWLEDGEBASE = EntitiesExtractor(embedding_model_path=ModelPaths.WORD_EMBEDDING_MODELS_DIR,
                                      embedding_model_name='word2vec.100d.chicagocrimevis')
    KNOWLEDGEBASE.extract_from_knowledgebase(DataExtractionPaths.CHICAGO_CRIME_KNOWLEDGEBASE_PATH)

    def __init__(self, context):
        super().__init__(context)
        self.discourse_extractor = DiscourseExtractor(request=self.request,
                                                      discourse_history=self.CURR_VIS_ID_TO_HISTORY_ID)

    def __str__(self):
        s = super().__str__()
        s += 'State- ' + str(self.CURR_DIALOGUE_HISTORY) + '\n'
        return s