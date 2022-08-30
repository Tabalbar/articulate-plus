from dev.data_extractor.chicago_encyclopedia_extractor import ChicagoEncyclopediaExtractor
from dev.data_extractor.chicago_suntimes_neighborhoods_extractor import ChicagoSunTimesNeighborhoodsExtractor
from dev.data_extractor.cjp_news_articles_extractor import CJPNewsArticlesExtractor
from dev.data_extractor.cwb_chicago_extractor import CWBChicagoExtractor
from dev.data_extractor.data_extraction_paths import DataExtractionPaths
from model_paths import  ModelPaths
from dev.data_extractor.entitiesextractor import EntitiesExtractor
from dev.data_extractor.wikipedia_extractor import WikipediaExtractor

print("Extracting text from chicago encyclopedia...")
extractor = ChicagoEncyclopediaExtractor(output_target_file=DataExtractionPaths.CHICAGO_ENCYCLOPEDIA_TEXT_DATA_PATH)
# extractor.extract()

chicago_encyclopedia_phrases = extractor.load_entities(
    input_source_file=DataExtractionPaths.CHICAGO_ENCYCLOPEDIA_ENTITIES_PATH)
print("Completed extracting from chicago encyclopedia...")

print("Extracting text from chicago sun times...")
extractor = ChicagoSunTimesNeighborhoodsExtractor(
    output_target_file=DataExtractionPaths.CHICAGO_SUN_TIMES_NEIGHBORHOODS_TEXT_DATA_PATH)
# extractor.extract()
print("Completed extracting text from chicago sun times...")

print("Extracting text from cwb chicago...")
extractor = CWBChicagoExtractor(output_target_file=DataExtractionPaths.CWB_CHICAGO_TEXT_DATA_PATH)
# extractor.extract()
print("Completed extracting text from cwb chicago...")

print("Extracting text from cjp news articles...")
extractor = CJPNewsArticlesExtractor(
    input_source_file=DataExtractionPaths.CJP_NEWS_ARTICLES_RAW_PATH,
    output_target_file=DataExtractionPaths.CJP_NEWS_ARTICLES_TEXT_DATA_PATH)
# extractor.extract()
print("Completed extracting text from cjp news articles...")

print("Extracting from knowledgebase...")
extractor = EntitiesExtractor(embedding_model_path=ModelPaths.WORD_EMBEDDING_MODELS_DIR,
                              embedding_model_name='word2vec.100d.chicagocrimevis')
# extractor.extract_from_ontology()
extractor.extract_from_knowledgebase(DataExtractionPaths.CHICAGO_CRIME_KNOWLEDGEBASE_PATH)
knowledgebase_phrases = extractor.get_all_terms()
print("Completed extracting from knowledgebase...")

print("Merging all of the entities...")
phrases = set(chicago_encyclopedia_phrases)
_ = [phrases.add(phrase) for phrase in knowledgebase_phrases]
print("Completed merging all of the entities...")

print("Extracting text from wikipedia relevant to the entities", phrases)
extractor = WikipediaExtractor(input_source_file=DataExtractionPaths.WIKIPEDIA_JSON_DATA_PATH, \
                               topics=list(phrases), index_path=DataExtractionPaths.WIKIPEDIA_INDEX_PATH, \
                               output_target_file=DataExtractionPaths.WIKIPEDIA_ENTITY_DATA_PATH)

# extractor.extract()
# wikipedia_entities = extractor.load_entities(DataExtractionPaths.WIKIPEDIA_ENTITIES_PATH)
print("Completed extracting text from wikipedia")
