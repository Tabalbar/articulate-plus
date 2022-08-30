import abc
from abc import ABCMeta, abstractmethod


class Evaluator(metaclass=ABCMeta):
    __metaclass__ = abc.ABCMeta

    def __init__(self, evaluator_config):
        training_parameters = evaluator_config['training_parameters']
        self.k_cross_validation = training_parameters['k_cross_validation']
        self.max_sequence_length = training_parameters['max_sequence_length']
        self.max_queries = training_parameters['max_queries']
        self.batch_size = training_parameters['batch_size']
        self.classification_level = training_parameters['classification_level']

        embedding_parameters = evaluator_config['embedding_parameters']
        self.embedding_type = embedding_parameters['embedding_type']
        self.embedding_dim = embedding_parameters['embedding_dim']

        data_augmentation_parameters = evaluator_config['data_augmentation_parameters']
        self.augment_with_paraphrases = data_augmentation_parameters['augment_with_paraphrases']
        self.augment_with_slot_replacement = data_augmentation_parameters['augment_with_slot_replacement']
        self.augment_with_synonym_replacement = data_augmentation_parameters['augment_with_synonym_replacement']
        self.total_versions = data_augmentation_parameters['total_versions']

        if 'dialogue_history_parameters' in evaluator_config:
            dialogue_history_parameters = evaluator_config['dialogue_history_parameters']
            self.search_window_sizes = dialogue_history_parameters['search_window_sizes']

        if 'dialogue_act_parameters' in evaluator_config:
            dialogue_act_parameters = evaluator_config['dialogue_act_parameters']
            self.use_full_context_window = dialogue_act_parameters['use_full_context_window']

    @abstractmethod
    def evaluate(self):
        raise NotImplementedError
