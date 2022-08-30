import os
os.environ['CUDA_VISIBLE_DEVICES'] = '0'
os.environ["OMP_NUM_THREADS"] = '4'
os.environ["OPENBLAS_NUM_THREADS"] = '5'
os.environ["MKL_NUM_THREADS"] = '6'
os.environ["VECLIB_MAXIMUM_THREADS"] = '4'
os.environ["NUMEXPR_NUM_THREADS"] = '6'
os.environ["NUMEXPR_NUM_THREADS"] = '5'

from dev.corpus_extractor.corpus_extraction_paths import CorpusExtractionPaths
from dev.referring_expression_extraction_model.crf_model import CRFModel as RECRFModel
from dev.referring_expression_extraction_model.utils import LearningTypeConfig, UseEmbeddingConfig


base_path = CorpusExtractionPaths.REFERRING_EXPRESSION_EXTRACTION_AND_NAMED_ENTITIES_DATA_PATH
referring_expression_csv_files = []
for sbj in range(5, 21):
    target_csv_file = []
    for ver in range(0, 1):
        target_csv_file.append(base_path + 'subject' + str(sbj) + '_0.csv')
    referring_expression_csv_files.append(target_csv_file)

referring_expression_extraction_factory = RECRFModel()

for referring_expression_model in referring_expression_extraction_factory.train(
        source_task_csv_files=referring_expression_csv_files,
        target_task_csv_files=None,
        source_tag_type='RefExp_Tag',
        target_tag_type=None,
        learning_type=LearningTypeConfig.SINGLE_TASK_LEARNING,
        k_cross_validation=-1,
        iterations=300,
        embedding_type=UseEmbeddingConfig.USE_CRIME_EMBEDDING,
        batch_size=1024,
        max_seq_len=20,
        evaluate=False,
        embedding_dim=100):
    print("Completed training referring expression extraction model", referring_expression_model, "for production")
