from dev.dialogue_act_model.bagc_model import BAGCModel as DABAGCModel
from dev.dialogue_act_model.bilstmcrf_model import BILSTMCRFModel as DABILSTMCRFModel
from dev.dialogue_act_model.bldnn_model import BLDNNModel as DABLDNNModel
from dev.dialogue_act_model.cldnn_model import CLDNNModel as DACLDNNModel
from dev.dialogue_act_model.convfilter_model import CONVFILTERModel as DACONVFILTERModel
from dev.dialogue_act_model.crf_model import CRFModel as DACRFModel
from dev.dialogue_act_model.ldnn_model import LDNNModel as DALDNNModel
from .evaluator import Evaluator
from dev.statistical_significance.anova import ANOVA

import json


class DialogueActModelEvaluator(Evaluator):
    def __init__(self, evaluator_config):
        super().__init__(evaluator_config)

    def evaluate(self):
        all_results = {}
        for model_name, model, iterations in \
                [
                    ('CRF', DACRFModel(), 100),
                    ('BAGC', DABAGCModel(), 50),
                    ('LDNN', DALDNNModel(), 30),
                    ('BLDNN', DABLDNNModel(), 30),
                    ('CLDNN', DACLDNNModel(), 30),
                    ('CONVFILTER', DACONVFILTERModel(), 30),
                    ('BILSTMCRF', DABILSTMCRFModel(), 30)
                ]:

            print("\n")
            print("k cross validation", self.k_cross_validation)
            print("model name", model_name)
            print("iterations", iterations)
            print("classification level", self.classification_level)

            print("\n\nStarted " + str(
                self.k_cross_validation) + " - cross validation evaluation of dialogue act model " + model_name, model)
            for fold, (top_unseen_subjects, top_trained_model, bottom_unseen_data, bottom_trained_model) in enumerate(
                    model.train(
                        classification_level=self.classification_level,
                        k_cross_validation=self.k_cross_validation,
                        augment_with_paraphrases=self.augment_with_paraphrases,
                        augment_with_slot_replacement=self.augment_with_slot_replacement,
                        augment_with_synonym_replacement=self.augment_with_synonym_replacement,
                        embedding_type=self.embedding_type,
                        total_versions=self.total_versions,
                        use_tokenizer=True,
                        max_sequence_length=self.max_sequence_length,
                        max_queries=self.max_queries,
                        iterations=iterations,
                        evaluate=True)):
                print("Completed fold " + str(fold) + " with " + str(
                    self.k_cross_validation) + " -cross validation evaluation of " + model_name + ", top model " + \
                      str(top_trained_model) + ", bottom model " + str(bottom_trained_model) + "\n\n")
            all_results.update(model.all_results)

        with open('results/dialogue_act_model_evaluation.json', 'w') as f:
            json.dump(obj=all_results, indent=4, fp=f)

        target_metric='F1'
        model_names, model_results = zip(*[(model, [model_result[target_metric] for model_result in all_model_results])
                                           for model, all_model_results in all_results.items() if 'top_level' in model])
        ANOVA.write_as_csv(model_names=model_names, model_results=model_results, alpha=0.05,
                           output_file_name='results/top_level_dialogue_act_model_evaluation_anova_tukey.csv')

        model_names, model_results = zip(*[(model, [model_result[target_metric] for model_result in all_model_results])
                                           for model, all_model_results in all_results.items() if 'bottom_level' in model])
        ANOVA.write_as_csv(model_names=model_names, model_results=model_results, alpha=0.05,
                           output_file_name='results/bottom_level_dialogue_act_model_evaluation_anova_tukey.csv')

        model_names, model_results = zip(*[(model, [model_result[target_metric] for model_result in all_model_results])
                                           for model, all_model_results in all_results.items() if 'two_level' in model])
        ANOVA.write_as_csv(model_names=model_names, model_results=model_results, alpha=0.05,
                           output_file_name='results/two_level_dialogue_act_model_evaluation_anova_tukey.csv')