from dev.text_tokenizer_pipeline import TextProcessingUtils
from ..rule import Rule
from ..shared_discourse_extractor import SharedDiscourseExtractor
from ..reference_extractor import ReferenceExtractor
from .statistics import Statistics

from collections import defaultdict
from copy import deepcopy

'''
- Step 4.1: process if the request is about creating a new vis from scratch (i.e., not from any template).

gold data:
1. generate smarthub id.
2. dialogue history mapping (smarthub id -> target vis id).
3. dialogue history mapping (target vis id -> smarthub id).
3. curr_spec added to dialogue history (shared).

statistics:
1. count number of created visualizations.
2. compare gold plot type to predicted plot type from curr spec.
'''


class VisualizationSpecificationStateUpdateRule(Rule):
    def __init__(self):
        super().__init__()

    def execute(self, rule_context):
        # extract target vis id from vis reference annotation and add to dialogue state mapping.
        #
        # assign latest available smarthub id to curr_spec id.
        _, _, _, target_vis_id, _, _, _ = ReferenceExtractor(rule_context.request.vis_reference_component). \
            extract_reference(which_one=0)

        history_id = rule_context.CURR_DIALOGUE_HISTORY.history_id
        rule_context.CURR_HISTORY_ID_TO_VIS_ID[history_id] = target_vis_id
        rule_context.CURR_VIS_ID_TO_HISTORY_ID[target_vis_id] = history_id
        rule_context.curr_spec.spec.plot_headline.id = history_id

    def should_execute(self, rule_context):
        # check if discourse type is creating new vis from scratch (i.e., not from any template).
        return rule_context.discourse_type == SharedDiscourseExtractor.NEW_VIS_NOT_FROM_EXISTING_TEMPLATE


class ExtractVisualizationSpecificationPropertiesRule(Rule):
    def __init__(self):
        super().__init__()

    def execute(self, rule_context):
        _, _, _, _, _, _, properties = ReferenceExtractor(rule_context.request.vis_reference_component).\
            extract_reference(which_one=0)

        gold_properties = [property.replace('_','').lower() for property in
                                                sorted(properties.replace('[','').replace(']','').split(';'))]

        rule_context.request.gold_properties = [property if '@@@' not in property else property.split('@@@')[0]
                                                for property in gold_properties]

    def should_execute(self, rule_context):
        # check if discourse type is creating new vis from scratch (i.e., not from any template).
        return rule_context.discourse_type == SharedDiscourseExtractor.NEW_VIS_NOT_FROM_EXISTING_TEMPLATE


class VisualizationSpecificationPropertiesStatisticsRule(Rule):
    @staticmethod
    def extract_slots_from_properties(properties, rule_context):
        processed_properties = list(set([TextProcessingUtils.clean_text(text=property, use_lemmas=True)
                                         for property in properties]))

        return [property for property in processed_properties if rule_context.KNOWLEDGEBASE.
            get_data_attribute_name(property) is not None]

    @staticmethod
    def determine_quartile(percentage):
        if percentage == 0.0:
            return 0.0

        if percentage < 0.25:
            return 0.25

        if percentage < 0.50:
            return 0.50

        if percentage < 0.75:
            return 0.75

        if percentage <= 1.0:
            return 1.0

    def execute(self, rule_context):
        match_distribution = Statistics.established_reference_phrases_match_distribution.distributions[-1]
        frequency_distribution = Statistics.established_reference_phrases_frequency_distribution.distributions[-1]
        error_distribution = Statistics.established_reference_phrases_slot_error_distribution.distributions[-1]

        match_distribution.total_labels += len(rule_context.request.gold_properties)

        gold_unmatched_slots = VisualizationSpecificationPropertiesStatisticsRule.\
            extract_slots_from_properties(rule_context.request.gold_properties, rule_context)
        gold_unmatched_slots_cpy = deepcopy(gold_unmatched_slots)
        for slot in gold_unmatched_slots:
            if slot not in error_distribution.label_errors:
                error_distribution.label_errors[slot] = defaultdict(int)

        pred_unmatched_slots = VisualizationSpecificationPropertiesStatisticsRule.\
            extract_slots_from_properties(rule_context.request.pred_properties, rule_context)
        pred_unmatched_slots_cpy = deepcopy(pred_unmatched_slots)

        if not pred_unmatched_slots and not gold_unmatched_slots:
            frequency_distribution.pred_label_frequencies[1.0] += 1
            return

        if not gold_unmatched_slots:
            frequency_distribution.pred_label_frequencies[0.0] += 1
            return

        if not pred_unmatched_slots:
            frequency_distribution.pred_label_frequencies[0.0] += 1
            return

        curr_matches = 0
        matched_gold_idx = set()
        for pred_idx, pred_slot in enumerate(pred_unmatched_slots_cpy):
            for gold_idx, gold_slot in enumerate(gold_unmatched_slots_cpy):
                if gold_idx in matched_gold_idx:
                    continue
                if pred_slot in gold_slot or gold_slot in pred_slot:
                    match_distribution.total_labels_matched += 1
                    curr_matches += 1
                    matched_gold_idx.add(gold_idx)
                    gold_unmatched_slots.remove(gold_slot)
                    pred_unmatched_slots.remove(pred_slot)
                    break

        percent_matched = curr_matches / len(gold_unmatched_slots_cpy)
        quartile = VisualizationSpecificationPropertiesStatisticsRule.determine_quartile(percent_matched)
        frequency_distribution.pred_label_frequencies[quartile] += 1
        for unmatched in gold_unmatched_slots:
            error_distribution.label_errors[unmatched][quartile] += 1

    def should_execute(self, rule_context):
        # properties exist only when the following is true:
        # - vis reference exists AND
        # - discourse type is creating vis AND
        # - properties annotated in vis reference.
        return rule_context.discourse_type == SharedDiscourseExtractor.NEW_VIS_FROM_EXISTING_TEMPLATE and \
               rule_context.request.gold_properties is not None and \
               len(rule_context.request.gold_properties) > 0


class VisualizationSpecificationDialogueHistoryAdditionStatisticsRule(Rule):
    def execute(self, rule_context):
        distribution = Statistics.established_reference_total_utterances[-1]
        distribution += 1

    def should_execute(self, rule_context):
        return rule_context.discourse_type == SharedDiscourseExtractor.NEW_VIS_NOT_FROM_EXISTING_TEMPLATE


class VisualizationSpecificationDialogueHistoryAdditionPlotTypeStatisticsRule(Rule):
    def execute(self, rule_context):
        _, _, _, _, gold_plot_type, _, _ = \
            ReferenceExtractor(rule_context.request.vis_reference_component).extract_reference(which_one=0)

        plot_type_mapping = {'bar chart': 'bar', 'line chart': 'line', 'heat map': 'heatmap',
                             'pie chart': 'pie'}
        pred_plot_type = plot_type_mapping[rule_context.curr_spec.spec.plot_headline.plot_type]

        distribution = Statistics.established_reference_plot_types_frequency_distribution.distributions[-1]
        distribution.pred_label_frequencies[pred_plot_type] += 1
        distribution.gold_label_frequencies[gold_plot_type] += 1

        distribution = Statistics.established_reference_plot_types_match_distribution.distributions[-1]
        distribution.total_labels += 1

        if pred_plot_type == gold_plot_type:
            distribution.total_labels_matched += 1
        else:
            distribution = Statistics.established_reference_plot_types_error_distribution.distributions[-1]
            if gold_plot_type not in distribution.label_errors:
                distribution.label_errors[gold_plot_type] = defaultdict(int)
            distribution.label_errors[gold_plot_type][pred_plot_type] += 1

    def should_execute(self, rule_context):
        return rule_context.discourse_type == SharedDiscourseExtractor.NEW_VIS_NOT_FROM_EXISTING_TEMPLATE
