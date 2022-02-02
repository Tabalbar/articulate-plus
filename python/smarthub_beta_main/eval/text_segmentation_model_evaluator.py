# Note: you must install dedupe-hcluster 0.3.8 for python3 to run this code (segeval needs it)
import json

import segeval
from collections import defaultdict

from dev.dialogue_act_model.bagc_model import BAGCModel as DABAGCModel
from dev.dialogue_act_model.bilstmcrf_model import BILSTMCRFModel as DABILSTMCRFModel
from dev.dialogue_act_model.bldnn_model import BLDNNModel as DABLDNNModel
from dev.dialogue_act_model.cldnn_model import CLDNNModel as DACLDNNModel
from dev.dialogue_act_model.convfilter_model import CONVFILTERModel as DACONVFILTERModel
from dev.dialogue_act_model.crf_model import CRFModel as DACRFModel
from dev.dialogue_act_model.ldnn_model import LDNNModel as DALDNNModel
from dev.text_segmentation_model.gold_text_segmenter import GoldTextSegmenter
from dev.text_segmentation_model.text_segmenter import TextSegmenter
from dev.statistical_significance.anova import ANOVA
from .evaluator import Evaluator
from dev.text_segmentation_model.segmentation_metrics import SegmentationMetrics


class TextSegmentationModelEvaluator(Evaluator):
    def __init__(self, evaluator_config):
        super().__init__(evaluator_config)

    def evaluate(self):
        all_results = defaultdict(list)

        # instantiate gold segmenter for getting our gold standard segments
        gold_text_segmenter = GoldTextSegmenter()
        # now get the gold standard segments. We will use these as the "expected" segments for evaluation.
        gold_segments_by_subject = gold_text_segmenter.get_segments_by_subject(unseen_subjects=None, fold=-1)
        # also get the gold standard utterances for each subject.
        # we need to use these to simulate online streaming to our text segmenter DialogueActModel.
        corpus_utterances = gold_text_segmenter.get_utterances_by_subject()

        for model_name, model, iterations in [
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
                self.k_cross_validation) + " - cross validation evaluation of incremental segmentation model " +
                  model_name, model)
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

                print("\n\nProcessing fold " + str(fold + 1) + " using model " + model_name + "\n\n")

                unseen_subjects_norm = ['subject' + str(subject + 5) for subject in top_unseen_subjects]

                text_segmenter = TextSegmenter(corpus_utterances, top_trained_model, bottom_trained_model, model)

                # run our text segmentation model and store the segments
                print("\n\nStarted running segmenter")
                segments_by_subject = text_segmenter.get_segments_by_subject(unseen_subjects_norm, fold=fold)
                print("Completed running segmenter\n\n")

                # build the boundaries for corpus (gold standard) and incremental (boundaries produced by our model)
                gold_segments = []
                segments = []
                for subject in unseen_subjects_norm:
                    gold_segments += gold_segments_by_subject[subject]
                    segments += segments_by_subject[subject]

                # compute common text segmentation performance evaluations (pk, window diff, precision, recall,
                # fmeasure, etc.)
                metrics = SegmentationMetrics(ytrue=gold_segments, ypred=segments)
                statistics = metrics.statistics()
                boundary_similarity, segmentation_similarity, window_diff, pk, precision, recall, f1, near_misses, \
                full_misses, boundary_matches, boundaries, additions, substitutions = \
                    metrics.boundary_similarity(), metrics.segmentation_similarity(), metrics.window_diff(), \
                    metrics.pk(), metrics.precision(), metrics.recall(), metrics.f1(), statistics['near_misses'], \
                    statistics['full_misses'], statistics['boundary_matches'], statistics['boundaries'], \
                    statistics['additions'], statistics['substitutions']

                print("\n\nResults - " + model_name + ", Fold: " + str(fold + 1))
                print("boundary_similarity", boundary_similarity)
                print("segmentation_similarity", segmentation_similarity)
                print("window_diff", window_diff)
                print("pk", pk)
                print("precision", precision)
                print("recall", recall)
                print("f1", f1)
                print("near_misses", near_misses)
                print("full_misses", full_misses)
                print("boundary_matches", boundary_matches)
                print("boundaries", boundaries)
                print("additions", additions)
                print("substitutions", substitutions)

                all_results[model_name].append(
                    {
                        'boundary_similarity': boundary_similarity,
                        'segmentation_similarity': segmentation_similarity,
                        'window_diff': window_diff,
                        'pk': pk,
                        'precision': precision,
                        'recall': recall,
                        'f1': f1,
                        'near_misses': near_misses,
                        'full_misses': full_misses,
                        'boundary_matches': boundary_matches,
                        'boundaries': boundaries,
                        'additions': additions,
                        'substitutions': substitutions
                    }
                )

        print(model_name, "--- Evaluation Summary for", self.k_cross_validation, "-cross validation")
        with open('results/text_segmentation_model_evaluation.json', 'w') as f:
            json.dump(obj=all_results, indent=4, fp=f)

        target_metrics = ['pk', 'window_diff', 'f1', 'near_misses', 'full_misses', 'boundary_matches']
        for target_metric in target_metrics:
            model_names, model_results = zip(*[(model, [model_result[target_metric] for model_result
                                                        in all_model_results]) for model, all_model_results
                                               in all_results.items()])
            ANOVA.write_as_csv(model_names=model_names, model_results=model_results, alpha=0.05,
                               output_file_name='results/text_segmentation_model_evaluation_anova_tukey' +
                                                '_' + target_metric + '.csv')
            print("\n\n")
