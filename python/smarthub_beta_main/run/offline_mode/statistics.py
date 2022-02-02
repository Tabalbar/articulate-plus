from collections import defaultdict

import abc
from abc import ABCMeta


class DistributionList(metaclass=ABCMeta):
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        super().__init__()
        self.distributions = []

    @abc.abstractmethod
    def get_merged_totals(self):
        raise NotImplementedError()


class LabelFrequencyDistribution:
    def __init__(self):
        super().__init__()
        self.pred_label_frequencies = defaultdict(int)
        self.gold_label_frequencies = defaultdict(int)

    def __str__(self):
        s = ''
        if self.pred_label_frequencies:
            s += 'Pred distribution:\n'
            for pred_label, freq in self.pred_label_frequencies.items():
                s += 'Label: ' + str(pred_label) + ', Frequency: ' + str(freq) + '\n'
        if self.gold_label_frequencies:
            s += 'Gold distribution:\n'
            for gold_label, freq in self.gold_label_frequencies.items():
                s += 'Label: ' + str(gold_label) + ', Frequency: ' + str(freq) + '\n'
        return s


class LabelFrequencyDistributionList(DistributionList):
    def __init__(self):
        super().__init__()

    def get_merged_totals(self):
        pred_label_sum = defaultdict(int)
        gold_label_sum = defaultdict(int)
        for label_frequency_distribution in self.distributions:
            pred_label_frequencies = label_frequency_distribution.pred_label_frequencies
            for label, freq in pred_label_frequencies.items():
                pred_label_sum[label] += freq

            gold_label_frequencies = label_frequency_distribution.gold_label_frequencies
            for label, freq in gold_label_frequencies.items():
                gold_label_sum[label] += freq
        return pred_label_sum, gold_label_sum

    def __str__(self):
        pred_label_sum, gold_label_sum = self.get_merged_totals()

        s = ''
        if pred_label_sum:
            s += '\t\tPred freq distribution\n'
            for pred_label, freq in pred_label_sum.items():
                s += '\t\t\tOverall - Label: ' + str(pred_label) + ', Total Frequency: ' + str(freq) + \
                     ', Avg Frequency: ' + str(freq / len(self.distributions)) + '\n'

        if gold_label_sum:
            s += '\t\tGold freq distribution\n'
            for gold_label, freq in gold_label_sum.items():
                s += '\t\t\tOverall - Label: ' + str(gold_label) + ', Total Frequency: ' + str(freq) + \
                     ', Avg Frequency: ' + str(freq / len(self.distributions)) + '\n'
        return s


class LabelErrorDistribution:
    def __init__(self):
        super().__init__()
        self.label_errors = defaultdict(dict)

    def __str__(self):
        s = ''
        if self.label_errors:
            s += 'Label error distribution\n'
            for gold_label, pred_label_errors in self.label_errors.items():
                s += 'Gold label: ' + str(gold_label) + '\n'
                for pred_label, pred_freq in pred_label_errors.items():
                    s += 'Pred label: ' + str(pred_label) + ', Frequency: ' + str(pred_freq) + '\n'
        return s


class LabelErrorDistributionList(DistributionList):
    def __init__(self):
        super().__init__()

    def get_merged_totals(self):
        label_errors_sum = defaultdict(dict)
        for label_error_distribution in self.distributions:
            for gold_label, pred_label_errors in label_error_distribution.label_errors.items():
                for pred_label, pred_freq in pred_label_errors.items():
                    if pred_label not in label_errors_sum[gold_label]:
                        label_errors_sum[gold_label][pred_label] = 0
                    label_errors_sum[gold_label][pred_label] += pred_freq
        return label_errors_sum

    def __str__(self):
        label_errors_sum = self.get_merged_totals()

        s = ''
        if label_errors_sum:
            s += '\t\tLabel error distribution\n'
            for gold_label, pred_label_errors in label_errors_sum.items():
                s += '\t\t\tGold label: ' + str(gold_label) + '\n'
                for pred_label, pred_freq in pred_label_errors.items():
                    s += '\t\t\t\tOverall - Pred label: ' + str(pred_label) + ', Total Frequency: ' + str(pred_freq) + \
                         ', Avg Frequency: ' + str(pred_freq / len(self.distributions)) + '\n'
        return s


class LabelMatchDistribution:
    def __init__(self):
        super().__init__()
        self.total_labels_matched = 0
        self.total_labels = 0

    def __str__(self):
        s = 'Total labels matched: ' + str(self.total_labels_matched) + '\n'
        s += 'Total labels: ' + str(self.total_labels) + '\n'
        return s


class LabelMatchDistributionList(DistributionList):
    def __init__(self):
        super().__init__()

    def get_merged_totals(self):
        labels_matched, labels, percent = 0, 0, 0.0
        for label_match_distribution in self.distributions:
            if label_match_distribution.total_labels == 0:
                continue
            percent += (label_match_distribution.total_labels_matched / label_match_distribution.total_labels)
            labels_matched += label_match_distribution.total_labels_matched
            labels += label_match_distribution.total_labels

        avg_percent = percent / len(self.distributions)
        avg_labels_matched = labels_matched / len(self.distributions)
        avg_labels = labels / len(self.distributions)

        return avg_labels_matched, avg_labels, avg_percent

    def get_total(self):
        total_labels_matched, total_labels = 0, 0
        for label_match_distribution in self.distributions:
            total_labels_matched += label_match_distribution.total_labels_matched
            total_labels += label_match_distribution.total_labels
        return total_labels_matched, total_labels

    def __str__(self):
        #s = 'Label Matches\n'
        s = ''

        total_labels_matched, total_labels = self.get_total()
        s += '\t\tOverall totals\n'
        s += '\t\t\tOverall labels matched total: ' + str(total_labels_matched) + '\n'
        s += '\t\t\tOverall labels total: ' + str(total_labels) + '\n'

        avg_labels_matched, avg_labels, avg_percent = self.get_merged_totals()
        s += '\t\tOverall Averages\n'
        s += '\t\t\tOverall Avg labels matched: ' + str(avg_labels_matched) + '\n'
        s += '\t\t\tOverall Avg labels: ' + str(avg_labels) + '\n'
        s += '\t\t\tOverall Avg percent: ' + str(avg_percent) + '\n'

        return s


class Statistics:
    top_level_dialogue_acts_match_distribution = LabelMatchDistributionList()
    bottom_level_dialogue_acts_match_distribution = LabelMatchDistributionList()

    text_reference_distance_frequency_distribution = LabelFrequencyDistributionList()
    text_reference_target_vis_ids_match_distribution = LabelMatchDistributionList()
    text_reference_texts_match_distribution = LabelMatchDistributionList()

    gesture_reference_distance_frequency_distribution = LabelFrequencyDistributionList()
    gesture_reference_target_vis_ids_match_distribution = LabelMatchDistributionList()
    gesture_reference_texts_match_distribution = LabelMatchDistributionList()

    established_reference_plot_types_match_distribution = LabelMatchDistributionList()
    established_reference_plot_types_frequency_distribution = LabelFrequencyDistributionList()
    established_reference_plot_types_error_distribution = LabelErrorDistributionList()
    established_reference_phrases_match_distribution = LabelMatchDistributionList()
    established_reference_phrases_frequency_distribution = LabelFrequencyDistributionList()
    established_reference_phrases_slot_error_distribution = LabelErrorDistributionList()
    established_reference_total_utterances = []

    @staticmethod
    def reset_statistics():
        Statistics.top_level_dialogue_acts_match_distribution = LabelMatchDistributionList()
        Statistics.bottom_level_dialogue_acts_match_distribution = LabelMatchDistributionList()

        Statistics.text_reference_distance_frequency_distribution = LabelFrequencyDistributionList()
        Statistics.text_reference_target_vis_ids_match_distribution = LabelMatchDistributionList()
        Statistics.text_reference_texts_match_distribution = LabelMatchDistributionList()

        Statistics.gesture_reference_distance_frequency_distribution = LabelFrequencyDistributionList()
        Statistics.gesture_reference_target_vis_ids_match_distribution = LabelMatchDistributionList()
        Statistics.gesture_reference_texts_match_distribution = LabelMatchDistributionList()

        Statistics.established_reference_plot_types_match_distribution = LabelMatchDistributionList()
        Statistics.established_reference_plot_types_frequency_distribution = LabelFrequencyDistributionList()
        Statistics.established_reference_plot_types_error_distribution = LabelErrorDistributionList()
        Statistics.established_reference_phrases_match_distribution = LabelMatchDistributionList()
        Statistics.established_reference_phrases_frequency_distribution = LabelFrequencyDistributionList()
        Statistics.established_reference_phrases_slot_error_distribution = LabelErrorDistributionList()
        Statistics.established_reference_total_utterances = []

    @staticmethod
    def add_new_statistics():
        Statistics.top_level_dialogue_acts_match_distribution.distributions.append(LabelMatchDistribution())
        Statistics.bottom_level_dialogue_acts_match_distribution.distributions.append(LabelMatchDistribution())

        Statistics.text_reference_distance_frequency_distribution.distributions.append(LabelFrequencyDistribution())
        Statistics.text_reference_target_vis_ids_match_distribution.distributions.append(LabelMatchDistribution())
        Statistics.text_reference_texts_match_distribution.distributions.append(LabelMatchDistribution())

        Statistics.gesture_reference_distance_frequency_distribution.distributions.append(LabelFrequencyDistribution())
        Statistics.gesture_reference_target_vis_ids_match_distribution.distributions.append(LabelMatchDistribution())
        Statistics.gesture_reference_texts_match_distribution.distributions.append(LabelMatchDistribution())

        Statistics.established_reference_plot_types_match_distribution.distributions.append(LabelMatchDistribution())
        Statistics.established_reference_plot_types_frequency_distribution.distributions.append(
            LabelFrequencyDistribution())
        Statistics.established_reference_plot_types_error_distribution.distributions.append(LabelErrorDistribution())
        Statistics.established_reference_phrases_match_distribution.distributions.append(LabelMatchDistribution())

        distribution = LabelFrequencyDistribution()
        distribution.pred_label_frequencies[0.0] = 0
        distribution.pred_label_frequencies[0.25] = 0
        distribution.pred_label_frequencies[0.50] = 0
        distribution.pred_label_frequencies[0.75] = 0
        distribution.pred_label_frequencies[1.0] = 0
        Statistics.established_reference_phrases_frequency_distribution.distributions.append(distribution)

        Statistics.established_reference_total_utterances.append(0)

        Statistics.established_reference_phrases_slot_error_distribution.distributions.append(LabelErrorDistribution())

    @staticmethod
    def print_averages():
        s = 'Text References\n'
        s += '\tTarget Vis Id\n'
        s += Statistics.text_reference_target_vis_ids_match_distribution.__str__() + '\n'

        s += '\tDistance frequency\n'
        s += Statistics.text_reference_distance_frequency_distribution.__str__() + '\n'

        s += '\tText\n'
        s += Statistics.text_reference_texts_match_distribution.__str__() + '\n'

        s += 'Gesture References\n'
        s += '\tTarget Vis Id\n'
        s += Statistics.gesture_reference_target_vis_ids_match_distribution.__str__() + '\n'

        s += '\tDistance frequency\n'
        s += Statistics.gesture_reference_distance_frequency_distribution.__str__() + '\n'

        s += '\tText\n'
        s += Statistics.gesture_reference_texts_match_distribution.__str__() + '\n'

        s += 'Dialogue Acts\n'
        s += '\tTop Level\n'
        s += Statistics.top_level_dialogue_acts_match_distribution.__str__() + '\n'
        s += '\tBottom Level\n'
        s += Statistics.bottom_level_dialogue_acts_match_distribution.__str__() + '\n'

        s += 'Established References\n'
        s += '\tPhrases\n'
        s += '\t\tMatches\n'
        s += Statistics.established_reference_phrases_match_distribution.__str__() + '\n'
        s += '\t\tFrequency\n'
        s += Statistics.established_reference_phrases_frequency_distribution.__str__() + '\n'
        s += '\t\tError\n'
        s += Statistics.established_reference_phrases_slot_error_distribution.__str__() + '\n'
        s += '\tPlot Types\n'
        s += '\t\tMatches\n'
        s += Statistics.established_reference_plot_types_match_distribution.__str__() + '\n'
        s += '\t\tFrequency\n'
        s += Statistics.established_reference_plot_types_frequency_distribution.__str__() + '\n'
        s += '\t\tError\n'
        s += Statistics.established_reference_plot_types_error_distribution.__str__() + '\n'

        print(s)