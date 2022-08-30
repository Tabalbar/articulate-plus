from dev.data_extractor.chicago_encyclopedia_extractor import ChicagoEncyclopediaExtractor
from dev.data_extractor.data_extraction_paths import DataExtractionPaths
from model_paths import ModelPaths
from dev.data_extractor.entitiesextractor.entitiesextractor import EntitiesExtractor

print("Extracting phrases from chicago encyclopedia...")
extractor = ChicagoEncyclopediaExtractor(output_target_file=DataExtractionPaths.CHICAGO_ENCYCLOPEDIA_TEXT_DATA_PATH)
chicago_encyclopedia_phrases = extractor.load_entities(
    input_source_file=DataExtractionPaths.CHICAGO_ENCYCLOPEDIA_ENTITIES_PATH)
print("Completed extracting phrases from chicago encyclopedia...")

print("Extracting phrases from knowledgebase...")
extractor = EntitiesExtractor(embedding_model_path=ModelPaths.WORD_EMBEDDING_MODELS_DIR,
                              embedding_model_name='word2vec.100d.chicagocrimevis')
extractor.extract_from_knowledgebase(DataExtractionPaths.CHICAGO_CRIME_KNOWLEDGEBASE_PATH)
knowledgebase_phrases = extractor.get_all_terms()
print("Completed extracting phrases from knowledgebase...")

print("Merging all of the phrases...")
phrases = set(chicago_encyclopedia_phrases)
_ = [phrases.add(phrase) for phrase in knowledgebase_phrases]
print("Completed merging all of the phrases...")

# Uncomment below to generate wikipedia index (***CAUTION***: this will overwrite previous wikipedia index!!!)
'''print("Started indexing wikipedia using the phrases",phrases)
extractor = WikipediaExtractor(input_source_file=DataExtractionPaths.WIKIPEDIA_JSON_DATA_PATH,\
topics=list(phrases),index_path=DataExtractionPaths.WIKIPEDIA_INDEX_PATH,\
output_target_file=DataExtractionPaths.WIKIPEDIA_DATA_PATH)
extractor.index_by_article_titles()
print("Completed indexing wikipedia")'''
