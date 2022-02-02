from .context_based_corpus_entity_extractor import ContextBasedCorpusEntityExtractor
from .request_based_corpus_entity_extractor import RequestBasedCorpusEntityExtractor
from model_paths import ModelPaths
from ..data_extractor.data_extractor_utils import DataExtractorUtils


class CorpusFeatureExtractorUtils:
    embedding_model_path = ModelPaths.WORD_EMBEDDING_MODELS_DIR
    embedding_model_name = 'word2vec.100d.chicagocrimevis'
    entity_lookup, named_entities, regular_expressions = DataExtractorUtils.get_chicago_crime_data(
        embedding_model_path=embedding_model_path, embedding_model_name=embedding_model_name)

    context_entity_extractor = \
        ContextBasedCorpusEntityExtractor(
            named_entities=named_entities,
            regular_expressions=regular_expressions,
            entity_lookup=entity_lookup)

    request_entity_extractor = \
        RequestBasedCorpusEntityExtractor(
            named_entities=named_entities,
            regular_expressions=regular_expressions,
            entity_lookup=entity_lookup)

    @staticmethod
    def get_context_based_corpus_entity_extractor(embedding_model_path=None, embedding_model_name=None):
        if not embedding_model_path or embedding_model_path == CorpusFeatureExtractorUtils.embedding_model_path:
            return CorpusFeatureExtractorUtils.context_entity_extractor
        if not embedding_model_name or embedding_model_name == CorpusFeatureExtractorUtils.embedding_model_name:
            return CorpusFeatureExtractorUtils.context_entity_extractor

        CorpusFeatureExtractorUtils.embedding_model_path = embedding_model_path
        CorpusFeatureExtractorUtils.entity_lookup, CorpusFeatureExtractorUtils.named_entities, \
            CorpusFeatureExtractorUtils.regular_expressions = \
                DataExtractorUtils.get_chicago_crime_data(embedding_model_path, embedding_model_name)

        CorpusFeatureExtractorUtils.context_entity_extractor = ContextBasedCorpusEntityExtractor(
            named_entities=CorpusFeatureExtractorUtils.named_entities,
            regular_expressions=CorpusFeatureExtractorUtils.regular_expressions,
            entity_lookup=CorpusFeatureExtractorUtils.entity_lookup)
        return CorpusFeatureExtractorUtils.context_entity_extractor

    @staticmethod
    def get_request_based_corpus_entity_extractor(embedding_model_path=None, embedding_model_name=None):
        if not embedding_model_path or embedding_model_path == CorpusFeatureExtractorUtils.embedding_model_path:
            return CorpusFeatureExtractorUtils.request_entity_extractor
        if not embedding_model_name or embedding_model_name == CorpusFeatureExtractorUtils.embedding_model_name:
            return CorpusFeatureExtractorUtils.request_entity_extractor

        CorpusFeatureExtractorUtils.embedding_model_path = embedding_model_path
        CorpusFeatureExtractorUtils.entity_lookup, CorpusFeatureExtractorUtils.named_entities, \
            CorpusFeatureExtractorUtils.regular_expressions = \
                DataExtractorUtils.get_chicago_crime_data(embedding_model_path, embedding_model_name)

        CorpusFeatureExtractorUtils.request_entity_extractor = RequestBasedCorpusEntityExtractor(
            named_entities=CorpusFeatureExtractorUtils.named_entities,
            regular_expressions=CorpusFeatureExtractorUtils.regular_expressions,
            entity_lookup=CorpusFeatureExtractorUtils.entity_lookup)

        return CorpusFeatureExtractorUtils.request_entity_extractor
