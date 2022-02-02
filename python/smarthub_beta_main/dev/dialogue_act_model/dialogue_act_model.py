import copy
import pickle
from abc import ABCMeta, abstractmethod
from os import path
from collections import defaultdict
from collections import Counter

import numpy as np
from sklearn_crfsuite import metrics

from .level import Level
from .utils import ClassificationLevelConfig, UseEmbeddingConfig
from ..corpus_data_augmentor.utils import Utils
from model_paths import ModelPaths

'''This is the base class Model:
	init:
		1. Note: the name should be "BAGC", or "CRF", or "LDNN", etc.
	train:
		1. Either you can train top level classifier (classification_level=ClassificationLevelConfig.TOP_LEVEL)
		which means to classify as request vs nonrequest (i.e.,'merged' or 'setup' or 'conclusion') or as bottom level
		classifier (ClassificationLevelConfig.BOTTOM_LEVEL) (i.e., classify as 'createvis', 'modifyvis', 
		'preferencebased', 'factbased', 'clarification', 'winmgmt') or two level classification 
		(ClassificationLevelConfig.TWO_LEVEL)

		2. You can train using all the training data (i.e., k_cross_validation=-1), or a single train and test split
		(k_cross_validation=1) or set to any larger positive integer (i.e., k_cross_validation=5 generates 5-fold 
		cross validation)
        Note: splits are across the 16 subjects, not the actual utterances themselves (i.e.,
			one sample 5-fold split could be: training=[1,2,3,4,5,6,7,8,9,10,11],test=[12,13,14,15,16])

		3. The use_paraphrasing=True indicates using augmented corpus with AUGX multiplier = total_versions.
		Note: total_versions=10 means you have 10 X more subjects (i.e., 160 subjects).

		4. The embedding_model_path is the path to a word embedding weight matrix. Note that
		'word2vec.100d.chicagocrimevis.wv.pkl' is the custom trained word embedding on chicago crime vis text,
		but you could set it to standard pre-trained word embedding model, or even set it to None (in the case
		of deep learnign model ONLY) to allow the model to learn it while training.

		5. The use_tokenizer=True flag means to use the rule-based semantic slot filling custom built for the 
		chicagocrimevis corpus. Leveraging it will tokenize all kinds of mutli-expression words 
		(e.g., "river north" instead of "river", "north").
'''


class DialogueActModel(metaclass=ABCMeta):
    __metaclass__ = ABCMeta

    def __init__(self, name, is_sequence_model=False):
        self._name = Level(name, name)
        self._tokenizer = Level()
        self._tag2idx = Level()
        self._idx2tag = Level()
        self._classes = Level()
        self._embedding_weights = Level()
        self._vocab_size = Level()
        self._feature_extractor = Level()
        self._is_sequence_model = is_sequence_model
        self._model_base_path = ModelPaths.DIALOGUE_ACT_MODELS_DIR
        self.all_results = defaultdict(list)

    def get_tokenizer(self):
        return self._tokenizer

    def set_tokenizer(self, tokenizer):
        self._tokenizer = copy.deepcopy(tokenizer)

    def get_tag2idx(self):
        return self._tag2idx

    def set_tag2idx(self, tag2idx):
        self._tag2idx = copy.deepcopy(tag2idx)

    def get_idx2tag(self):
        return self._idx2tag

    def set_idx2tag(self, idx2tag):
        self._idx2tag = copy.deepcopy(idx2tag)

    def get_classes(self):
        return self._classes

    def set_classes(self, CLASSES):
        self._classes = copy.deepcopy(CLASSES)

    def get_vocab_size(self):
        return self._vocab_size

    def set_vocab_size(self, vocab_size):
        self._vocab_size = copy.deepcopy(vocab_size)

    def get_embedding_weights(self):
        return self._embedding_weights

    def set_embedding_weights(self, embedding_weights):
        self._embedding_weights = copy.deepcopy(embedding_weights)

    def get_max_sequence_length(self):
        return self._max_sequence_length

    def set_max_sequence_length(self, max_sequence_length):
        self._max_sequence_length = max_sequence_length

    def get_max_queries(self):
        return self._max_queries

    def set_max_queries(self, max_queries):
        self._max_queries = max_queries

    def get_classification_level(self):
        return self._classification_level

    def set_classification_level(self, classification_level):
        self._classification_level = classification_level

    def get_k_cross_validation(self):
        return self._k_cross_validation

    def set_k_cross_validation(self, k_cross_validation):
        self._k_cross_validation = k_cross_validation

    def get_total_versions(self):
        return self._total_versions

    def set_total_versions(self, total_versions):
        self._total_versions = total_versions

    def get_use_embedding_model(self):
        return self._use_embedding_model

    def set_use_embedding_model(self, use_embedding_model):
        self._use_embedding_model = use_embedding_model

    def get_use_paraphrasing(self):
        return self._use_paraphrasing

    def set_use_paraphrasing(self, use_paraphrasing):
        self._use_paraphrasing = use_paraphrasing

    def get_corpus_path(self):
        return self._corpus_path

    def set_corpus_path(self, corpus_path):
        self._corpus_path = corpus_path

    def get_feature_extractor(self):
        return self._feature_extractor

    def set_feature_extractor(self, feature_extractor):
        self._feature_extractor = copy.deepcopy(feature_extractor)

    def get_is_sequence_model(self):
        return self._is_sequence_model

    def set_is_sequence_model(self, is_sequence_model):
        self._is_sequence_model = is_sequence_model

    def train(self,
              classification_level=ClassificationLevelConfig.TOP_LEVEL,
              k_cross_validation=True,
              augment_with_paraphrases=True,
              augment_with_slot_replacement=True,
              augment_with_synonym_replacement=False,
              total_versions=10,
              embedding_type=UseEmbeddingConfig.USE_CRIME_EMBEDDING,
              use_tokenizer=True,
              max_sequence_length=None,
              max_queries=10,
              iterations=10,
              evaluate=False):

        self._classification_level = classification_level
        self._k_cross_validation = k_cross_validation
        self._total_versions = total_versions

        self._use_paraphrasing = False;
        if augment_with_paraphrases or augment_with_slot_replacement or augment_with_synonym_replacement:
            self._use_paraphrasing = True
        self._corpus_path = Utils.get_corpus_path(
            augment_with_paraphrases=augment_with_paraphrases,
            augment_with_slot_replacement=augment_with_slot_replacement,
            augment_with_synonym_replacement=augment_with_synonym_replacement,
            total_versions=total_versions)

        if embedding_type == UseEmbeddingConfig.USE_CRIME_EMBEDDING:
            self._embedding_model_path = ModelPaths.WORD_EMBEDDING_MODELS_DIR
            self._embedding_model_name = 'word2vec.100d.chicagocrimevis.pkl'
            self._use_embedding_model = True

        elif embedding_type == UseEmbeddingConfig.USE_PRETRAINED_EMBEDDING:
            self._embedding_model_path = ModelPaths.WORD_EMBEDDING_MODELS_DIR
            self._embedding_model_name = 'word2vec.glove.6b.100d.pkl'
            self._use_embedding_model = True

        elif embedding_type == UseEmbeddingConfig.USE_NO_EMBEDDING:
            self._embedding_model_path = ModelPaths.WORD_EMBEDDING_MODELS_DIR
            self._embedding_model_name =  'word2vec.100d.chicagocrimevis.pkl'
            self._use_embedding_model = False

        self._use_tokenizer = use_tokenizer

        self._max_sequence_length = max_sequence_length
        self._max_queries = max_queries
        self._iterations = iterations

    @abstractmethod
    def predict(self, top_level_trained_model, bottom_level_trained_model, context_utterances):
        pass

    @abstractmethod
    def _get_train_no_split(self):
        pass

    @abstractmethod
    def _get_single_train_test_split(self):
        pass

    @abstractmethod
    def _get_cross_validation_train_test_split(self):
        pass

    @abstractmethod
    def _get_data(self):
        pass

    '''
    load the appropriate model (if it exists) depending on if it is a top level or bottom level classifier.
    '''

    def load_model(self, which_level, subjects=None, fold=0):
        if which_level == ClassificationLevelConfig.TOP_LEVEL:
            if subjects is not None:
                model_path = self._model_base_path + '_'.join(
                    [str(s) for s in subjects]) + '_' + self._name.get_top_level() + '_' + str(fold) + '.pkl'
            else:
                model_path = self._model_base_path + self._name.get_top_level() + '_' + str(fold) + '.pkl'

            if path.isfile(model_path):
                print("Loading", model_path)
                trained_model = pickle.load(open(model_path, 'rb'))
                return trained_model

        elif which_level == ClassificationLevelConfig.BOTTOM_LEVEL:
            if subjects is not None:
                model_path = self._model_base_path + '_'.join(
                    [str(s) for s in subjects]) + '_' + self._name.get_bottom_level() + '_' + str(fold) + '.pkl'
            else:
                model_path = self._model_base_path + self._name.get_bottom_level() + '_' + str(fold) + '.pkl'

            if path.isfile(model_path):
                print("Loading", model_path)
                trained_model = pickle.load(open(model_path, 'rb'))
                return trained_model

        return None

    '''
    save the appropriate model (if it exists) depending on if it is a top level or bottom level classifier.
    '''

    def save_model(self, which_level, trained_model, subjects=None, fold=0):
        if which_level == ClassificationLevelConfig.TOP_LEVEL:
            if subjects is not None:
                model_path = self._model_base_path + '_'.join(
                    [str(s) for s in subjects]) + '_' + self._name.get_top_level() + '_' + str(fold) + '.pkl'
            else:
                model_path = self._model_base_path + self._name.get_top_level() + '_' + str(fold) + '.pkl'
            print("Saving", model_path)
            pickle.dump(trained_model, open(model_path, 'wb'))

        elif which_level == ClassificationLevelConfig.BOTTOM_LEVEL:
            if subjects is not None:
                model_path = self._model_base_path + '_'.join(
                    [str(s) for s in subjects]) + '_' + self._name.get_bottom_level() + '_' + str(fold) + '.pkl'
            else:
                model_path = self._model_base_path + self._name.get_bottom_level() + '_' + str(fold) + '.pkl'
            print("Saving", model_path)
            pickle.dump(trained_model, open(model_path, 'wb'))

    @abstractmethod
    def get_model_architecture(self, words, tags, which_level):
        raise NotImplementedError

    '''
    We are indifferent about 'setup' and 'conclusion' since they are not requests. So just assign them to 'other'.
    '''

    @staticmethod
    def update_setup_and_conclusion_to_other(y, setup_key='setup', conclusion_key='conclusion', replace_key='other'):
        y_norm = []
        for cntxt in y:
            new_cntxt = []
            for label in cntxt:
                if label == setup_key or label == conclusion_key:
                    new_cntxt.append(replace_key)
                else:
                    new_cntxt.append(label)
            y_norm.append(new_cntxt)
        return y_norm

    '''
    Every context must contain at least one request. If not, then we randomly assign the
    approximate middle utterance to a random label. Similarly if there is more than 1
    request, then simply remove one request.
    '''

    @staticmethod
    def adjust_request_if_missing_or_too_many_in_context(y, requests, tag2idx, setup_key='setup',
                                                         conclusion_key='conclusion', \
                                                         replace_key='other'):
        y_norm = []
        for cntxt in y:
            requests_mapping = {}
            for idx, label in enumerate(cntxt):
                if label in requests:
                    requests_mapping[idx] = label

            # if context is missing a request assign approx middle utterance to random request
            if len(requests_mapping) == 0:
                cntxt[int(len(cntxt) / 2)] = np.random.choice(requests)
                y_norm.append(cntxt)

            # cntxt should only have a single request so remove excessive ones.
            elif len(requests_mapping) > 1:
                # we can get index of each utterance assigned request label
                # from this list, we select a random index as the one request we keep.
                target_idx = np.random.choice(list(requests_mapping.keys()))

                for idx in requests_mapping.keys():
                    # found the one utterance we are keeping as a request so skip
                    if idx == target_idx:
                        continue

                    # otherwise update to 'other' to remove the excessive request label
                    cntxt[idx] = replace_key
                y_norm.append(cntxt)

            else:

                # there is only one and exactly one request so do nothing
                y_norm.append(cntxt)
        return y_norm

    '''
    transform a list of labels (y) to a list of lists (each one representing a sequence).

    For example, if y = ['setup','clarification','conclusion','fact-based','conclusion'], then one
    plausibly this transformation would result in y = [['setup', 'clarification', 'conclusion'],
    ['fact-based','conclusion']] and hence segmenting into distinct CARs.
    '''

    @staticmethod
    def transform_to_sequence(sequence_spans, y):
        y_sequence = []
        for span in sequence_spans:
            y_sequence.append(y[span])
        return y_sequence

    '''
    Builds dictionary of performance results
    '''

    def _compute_performance(self, name, y_test, y_pred, idx2tag, performance_dict=None,
            filter_class_labels=['PAD', 'UNK'], weight_type='weighted'):
        if filter_class_labels:
            target_name_indices, target_names = zip(
                *[(idx, tag) for idx, tag in sorted(idx2tag.items(), key=lambda kv: kv[0]) if
                  tag not in filter_class_labels])

            precision = metrics.flat_precision_score(
                y_test, y_pred, average=weight_type, labels=target_name_indices, zero_division=0)
            recall = metrics.flat_recall_score(
                y_test, y_pred, average=weight_type, labels=target_name_indices, zero_division=0)
            f1 = metrics.flat_f1_score(
                y_test, y_pred, average=weight_type, labels=target_name_indices, zero_division=0)
            accuracy = metrics.flat_accuracy_score(y_test, y_pred)

            print(
                metrics.flat_classification_report(
                    y_test, y_pred, zero_division=0, target_names=target_names, labels=target_name_indices, digits=2
                )
            )
        else:
            precision = metrics.flat_precision_score(
                y_test, y_pred, average=weight_type, zero_division=0)
            recall = metrics.flat_recall_score(
                y_test, y_pred, average=weight_type, zero_division=0)
            f1 = metrics.flat_f1_score(
                y_test, y_pred, average=weight_type, zero_division=0)
            accuracy = metrics.flat_accuracy_score(y_test, y_pred)

            print(metrics.flat_classification_report(y_test, y_pred, zero_division=0, digits=2))

        if not performance_dict:
            performance_dict = {
                'Precision': float(0),
                'Recall': float(0),
                'F1': float(0),
                'Accuracy': float(0),
            }

        performance_dict['Precision'] += precision
        performance_dict['Recall'] += recall
        performance_dict['F1'] += f1
        performance_dict['Accuracy'] += accuracy

        self.all_results[name].append(
            {'Precision':precision,
             'Recall':recall,
             'F1':f1,
             'Accuracy':accuracy}
        )

        return performance_dict

    '''
    prints the contents of a performance dictionary.
    '''

    def _print_performance(self, fold, performance_dict, name):
        if not performance_dict:
            return
        print("\n\nSummary: " + name + ", Fold: " + str(fold))
        print('Precision', performance_dict['Precision'] / self._k_cross_validation)
        print('Recall', performance_dict['Recall'] / self._k_cross_validation)
        print('F1', performance_dict['F1'] / self._k_cross_validation)
        print('Accuracy', performance_dict['Accuracy'] / self._k_cross_validation)

    def get_class_weight(self, y, pad_idx=0, normalize=False):
        support = Counter(y.flatten())
        del support[pad_idx]
        total_classes = len(support)
        total_support = sum(support.values())

        minority_weighted = {curr_class : total_support / (class_support * total_classes)
                             for curr_class,class_support in support.items()}

        if normalize:
            max_class_support = max(minority_weighted.values())
            minority_weighted = {curr_class: class_support / max_class_support for curr_class, class_support in
                             minority_weighted.items()}
        minority_weighted[pad_idx] = 0
        minority_weighted = [curr_class[1] for curr_class in sorted(minority_weighted.items(), key=lambda x: x[0])]

        return minority_weighted