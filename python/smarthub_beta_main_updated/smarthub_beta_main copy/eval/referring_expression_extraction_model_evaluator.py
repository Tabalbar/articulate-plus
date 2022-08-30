from dev.corpus_extractor.corpus_extraction_paths import CorpusExtractionPaths
from dev.referring_expression_extraction_model.bertcrf_model import BERTCRFModel as REBERTCRFModel
from dev.referring_expression_extraction_model.bilstmcrf_model import BILSTMCRFModel as REBILSTMCRFModel
from dev.referring_expression_extraction_model.crf_model import CRFModel as RECRFModel
from dev.referring_expression_extraction_model.utils import LearningTypeConfig
from dev.statistical_significance.anova import ANOVA
from .evaluator import Evaluator

import json

class ReferringExpressionExtractionModelEvaluator(Evaluator):
    def __init__(self, evaluator_config):
        super().__init__(evaluator_config)

        self.source_csv_files = []
        for sbj in range(5, 21):
            source_csv_file = []
            for ver in range(1, 10):
                source_csv_file.append(
                    CorpusExtractionPaths.REFERRING_EXPRESSION_EXTRACTION_AND_NAMED_ENTITIES_DATA_PATH + 'subject' +
                    str(sbj) + '_' + str(
                        ver) + '.csv')
            self.source_csv_files.append(source_csv_file)

        self.target_csv_files = []
        for sbj in range(5, 21):
            target_csv_file = []
            for ver in range(0, 1):
                target_csv_file.append(
                    CorpusExtractionPaths.REFERRING_EXPRESSION_EXTRACTION_AND_NAMED_ENTITIES_DATA_PATH + 'subject' +
                    str(sbj) + '_0.csv')
            self.target_csv_files.append(target_csv_file)

    def evaluate(self):
        all_results = {}
        for model_name, model, iterations, learning_type, source_files, target_files, source_tags, target_tags in [
            ('CRF_Single_Task',
             RECRFModel(),
             300,
             LearningTypeConfig.SINGLE_TASK_LEARNING,
             self.target_csv_files,
             None,
             'RefExp_Tag',
             None),

            ('BILSTMCRF_Single_Task',
             REBILSTMCRFModel(),
             20,
             LearningTypeConfig.SINGLE_TASK_LEARNING,
             self.target_csv_files,
             None,
             'RefExp_Tag',
             None),

            ('BILSTMCRF_Transfer_Task',
             REBILSTMCRFModel(),
             20,
             LearningTypeConfig.TRANSFER_TASK_LEARNING,
             self.source_csv_files,
             self.target_csv_files,
             'NER_Tag',
             'RefExp_Tag'),

            ('BILSTMCRF_Multi_Task',
             REBILSTMCRFModel(),
             20,
             LearningTypeConfig.MULTI_TASK_LEARNING,
             self.source_csv_files,
             self.target_csv_files,
             'NER_Tag',
             'RefExp_Tag'),

            ('BERTCRF_Single_Task',
             REBERTCRFModel(),
             20,
             LearningTypeConfig.SINGLE_TASK_LEARNING,
             self.target_csv_files,
             None,
             'RefExp_Tag',
             None),

            ('BERTCRF_Transfer_Task',
             REBERTCRFModel(),
             20,
             LearningTypeConfig.TRANSFER_TASK_LEARNING,
             self.source_csv_files,
             self.target_csv_files,
             'NER_Tag',
             'RefExp_Tag'),

            ('BERTCRF_Multi_Task',
             REBERTCRFModel(),
             20,
             LearningTypeConfig.MULTI_TASK_LEARNING,
             self.source_csv_files,
             self.target_csv_files,
             'NER_Tag',
             'RefExp_Tag')
        ]:

            print("\n")
            print("k cross validation", self.k_cross_validation)
            print("model name", model_name)
            print("iterations", iterations)
            print("learning type", learning_type)
            print("source tags", source_tags)
            print("target tags", target_tags)

            print("\n\nStarted " + str(
                self.k_cross_validation) + " - cross validation evaluation of referring expressions extraction model "
                  + model_name, model)
            for fold, trained_model in enumerate(model.train(
                    source_task_csv_files=source_files,
                    target_task_csv_files=target_files,
                    source_tag_type=source_tags,
                    target_tag_type=target_tags,
                    learning_type=learning_type,
                    k_cross_validation=self.k_cross_validation,
                    iterations=iterations,
                    embedding_type=self.embedding_type,
                    batch_size=self.batch_size,
                    max_seq_len=self.max_sequence_length,
                    evaluate=True,
                    embedding_dim=self.embedding_dim)):
                print("Completed fold " + str(fold) + " with " + str(
                    self.k_cross_validation) + " - cross validation evaluation of " \
                      + model_name + ", " + str(trained_model) + "\n\n")
            all_results.update(model.all_results)

        with open('results/referring_expression_extraction_model_evaluation.json', 'w') as f:
            json.dump(obj=all_results, indent=4, fp=f)

        target_metric = 'F1'
        model_names, model_results = zip(*[(model, [model_result[target_metric] for model_result in all_model_results])
                                           for model, all_model_results in all_results.items()])
        ANOVA.write_as_csv(model_names=model_names, model_results=model_results, alpha=0.05,
                           output_file_name='results/referring_expression_extraction_model_evaluation_anova_tukey.csv')
