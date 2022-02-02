from .chicago_encyclopedia_extractor import ChicagoEncyclopediaExtractor
from .data_extraction_paths import DataExtractionPaths
from .entitiesextractor import EntitiesExtractor


class DataExtractorUtils:

    @staticmethod
    def get_chicago_crime_data(embedding_model_path, embedding_model_name):
        print("Extracting entities from chicago encyclopedia...")
        extractor = ChicagoEncyclopediaExtractor(output_target_file=
            DataExtractionPaths.CHICAGO_ENCYCLOPEDIA_TEXT_DATA_PATH)
        chicago_encyclopedia_phrases = extractor.load_entities(
            input_source_file=DataExtractionPaths.CHICAGO_ENCYCLOPEDIA_ENTITIES_PATH)
        print("Completed entities phrases from chicago encyclopedia...[" + str(len(chicago_encyclopedia_phrases)) + "]")

        print("Extracting entities from knowledgebase...")
        entity_lookup = EntitiesExtractor(
            embedding_model_path=embedding_model_path, embedding_model_name=embedding_model_name)
        entity_lookup.extract_from_knowledgebase(DataExtractionPaths.CHICAGO_CRIME_KNOWLEDGEBASE_PATH)

        named_entities = []
        for term in entity_lookup.get_all_terms():
            entity_name = entity_lookup.get_name(term.lower())
            entity_value = term.lower()
            named_entities.append((entity_name, entity_value))
        print("Completed extracting entities from knowledgebase...[" + str(len(named_entities)) + "]")

        print("Starting extracting regular expressions from knowledgebase...")
        regular_expressions = [regular_expression_entity.get_value() for regular_expression_entity \
                               in entity_lookup.get_all_regular_expression_entities() if \
                               regular_expression_entity.get_data_attribute() is not None]
        print("Completed extracting regular expressions from knowledgebase...[" + str(len(regular_expressions)) + "]")

        print("Merging all of the entities...")
        for term in chicago_encyclopedia_phrases:
            entity_name = 'unknown'
            entity_value = term
            named_entities.append((entity_name, entity_value))
        print("Completed merging all of the entities...[" + str(len(named_entities)) + "]")

        return entity_lookup, named_entities, regular_expressions
