from collections import OrderedDict
from sklearn.model_selection import KFold
import numpy as np

from app import StateTracker, LanguageUnderstandingModels
from dev.corpus_feature_extractor import CorpusFeatureExtractorUtils
from dev.corpus_extractor.extractor import Extractor as CorpusExtractor
from dev.corpus_data_augmentor.utils import Utils as CorpusDataAugmentorUtils
from .evaluator import Evaluator

from run.offline_mode.rule_context import RuleContext
from run.offline_mode.rule_engine_factory import RuleEngineFactory
from run.offline_mode.statistics import Statistics


class SmarthubEvaluator(Evaluator):
    def __init__(self, evaluator_config):
        super().__init__(evaluator_config)

    def evaluate(self):
        input_processing_rules_engine, \
            language_model_prediction_rules_engine, \
            established_reference_rules_engine, \
            discourse_rules_engine, \
            create_vis_not_from_existing_template_discourse_rules_engine, \
            create_vis_from_existing_template_discourse_rules_engine, \
            existing_vis_discourse_rules_engine = RuleEngineFactory.build()

        corpus_path = CorpusDataAugmentorUtils.get_corpus_path(
            augment_with_paraphrases=self.augment_with_paraphrases,
            augment_with_slot_replacement=self.augment_with_slot_replacement,
            augment_with_synonym_replacement=self.augment_with_synonym_replacement,
            total_versions=self.total_versions)

        corpus_entity_extractor = CorpusFeatureExtractorUtils. \
            get_context_based_corpus_entity_extractor()
        entity_tokenizer = corpus_entity_extractor.get_tokenizer()

        LanguageUnderstandingModels.K_CROSS_VALIDATION = 5
        LanguageUnderstandingModels.TOTAL_SUBJECTS = 16
        RuleContext.ENTITY_TOKENIZER = entity_tokenizer

        for search_window_size in self.search_window_sizes:
            Statistics.reset_statistics()
            annotated_utterances_by_subject_with_processed_refexps = dict(
                CorpusExtractor.extract_from_json(corpus_path=corpus_path, process_refexps=True))
            history_id_to_vis_id = OrderedDict()
            vis_id_to_history_id = OrderedDict()
            dialogue_history = OrderedDict()

            k_fold = KFold(n_splits=LanguageUnderstandingModels.K_CROSS_VALIDATION, shuffle=True, random_state=7)
            X_p = np.zeros((LanguageUnderstandingModels.TOTAL_SUBJECTS,))
            y_p = np.zeros((LanguageUnderstandingModels.TOTAL_SUBJECTS,))

            for fold, (train, test) in enumerate(k_fold.split(X_p, y_p)):
                print("Fold: " + str(fold))
                RuleContext.FOLD = fold
                RuleContext.USE_FULL_CONTEXT_WINDOW_FOR_DA_PREDICTION = self.use_full_context_window
                Statistics.add_new_statistics()
                for subject in test:

                    if subject not in vis_id_to_history_id:
                        vis_id_to_history_id[subject] = OrderedDict()
                        vis_id_to_history_id[subject][-1] = -1
                    curr_vis_id_to_history_id = vis_id_to_history_id[subject]

                    if subject not in history_id_to_vis_id:
                        history_id_to_vis_id[subject] = OrderedDict()
                        history_id_to_vis_id[subject][-1] = -1
                    curr_history_id_to_vis_id = history_id_to_vis_id[subject]

                    if subject not in dialogue_history:
                        dialogue_history[subject] = StateTracker(search_window_size=search_window_size)
                    curr_dialogue_history = dialogue_history[subject]

                    print("\n\n*****SUBJECT*****", subject + 5)

                    RuleContext.CURR_VIS_ID_TO_HISTORY_ID = curr_vis_id_to_history_id
                    RuleContext.CURR_HISTORY_ID_TO_VIS_ID = curr_history_id_to_vis_id
                    RuleContext.CURR_DIALOGUE_HISTORY = curr_dialogue_history
                    for context_window in annotated_utterances_by_subject_with_processed_refexps[
                        'subject' + str(subject + 5) + '_0']:
                        rule_context = RuleContext(context_window)
                        rule_context = input_processing_rules_engine.execute(rule_context)
                        rule_context = language_model_prediction_rules_engine.execute(rule_context)
                        rule_context = established_reference_rules_engine.execute(rule_context)
                        rule_context = discourse_rules_engine.execute(rule_context)

                        # unable to determine discourse type when vis component does not exist.
                        if rule_context.discourse_type == -1:
                            continue

                        rule_context = create_vis_not_from_existing_template_discourse_rules_engine.\
                            execute(rule_context)
                        rule_context = create_vis_from_existing_template_discourse_rules_engine.execute(rule_context)
                        rule_context = existing_vis_discourse_rules_engine.execute(rule_context)
                        # print(rule_context)
                        # print("\n\n")

            print("Search window size: " + str(search_window_size))
            Statistics.print_averages()
