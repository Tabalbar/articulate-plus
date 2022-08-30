from dev.data_extractor.data_extraction_paths import DataExtractionPaths
from model_paths import ModelPaths
from dev.data_extractor.entitiesextractor import EntitiesExtractor

print("Start extracting from ontology...")
extractor = EntitiesExtractor(embedding_model_path=ModelPaths.WORD_EMBEDDING_MODELS_DIR,
                              embedding_model_name='word2vec.100d.chicagocrimevis')
extractor.extract_from_ontology(DataExtractionPaths.CHICAGO_CRIME_ONTOLOGY_PATH)
print("Completed extracting from ontology...")

print("Started storing knowledgebase")
extractor.store_knowledgebase(DataExtractionPaths.CHICAGO_CRIME_KNOWLEDGEBASE_PATH)
print("Completed storing knowledgebase")
