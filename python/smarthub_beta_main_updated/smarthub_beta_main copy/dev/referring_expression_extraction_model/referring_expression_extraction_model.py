import abc
from abc import ABCMeta
from sklearn_crfsuite import metrics
from collections import defaultdict, Counter

from .sequence_metrics import SequenceMetrics
from .utils import LearningTypeConfig
from .utils import UseEmbeddingConfig
from model_paths import ModelPaths


class ReferringExpressionExtractionModel(metaclass=ABCMeta):
    __metaclass__ = abc.ABCMeta

    def __init__(self, name=None):
        self._name = name
        self._model_base_path = ModelPaths.REFERRING_EXPRESSION_EXTRACTION_MODELS_DIR
        self.all_results = defaultdict(list)

    @abc.abstractmethod
    def train(self,
              source_task_csv_files,
              target_task_csv_files,
              source_tag_type,
              target_tag_type,
              learning_type=LearningTypeConfig.SINGLE_TASK_LEARNING,
              k_cross_validation=5,
              iterations=10,
              embedding_type=UseEmbeddingConfig.USE_CRIME_EMBEDDING,
              max_seq_len=None,
              batch_size=64,
              evaluate=False,
              embedding_dim=100):

        self._max_seq_len = max_seq_len

        self._learning_type = learning_type

        self._iterations = iterations

        self._k_cross_validation = k_cross_validation
        self._embedding_dim = embedding_dim

        self._batch_size = batch_size

        if self._k_cross_validation == -1:
            self._get_training_data_fn = self._get_train_no_split
        elif self._k_cross_validation == 1:
            self._get_training_data_fn = self._get_single_train_test_split
        else:
            self._get_training_data_fn = self._get_cross_validation_train_test_split

        if embedding_type == UseEmbeddingConfig.USE_CRIME_EMBEDDING:
            self._embedding_model_path = ModelPaths.WORD_EMBEDDING_MODELS_DIR + 'word2vec.100d.chicagocrimevis.pkl'
            self._use_embedding_model = True

        elif embedding_type == UseEmbeddingConfig.USE_PRETRAINED_EMBEDDING:
            self._embedding_model_path = ModelPaths.WORD_EMBEDDING_MODELS_DIR + 'word2vec.glove.6b.100d.pkl'
            self._use_embedding_model = True

        elif embedding_type == UseEmbeddingConfig.USE_NO_EMBEDDING:
            self._embedding_model_path = ModelPaths.WORD_EMBEDDING_MODELS_DIR + 'word2vec.100d.chicagocrimevis.pkl'
            self._use_embedding_model = False

    @abc.abstractmethod
    def predict(self, trained_model, utterance):
        pass

    @abc.abstractmethod
    def _get_train_no_split(self, datasets, tag_type, words, pos, tags):
        pass

    @abc.abstractmethod
    def _get_single_train_test_split(self, datasets, tag_type, words, pos, tags):
        pass

    @abc.abstractmethod
    def _get_cross_validation_train_test_split(self, datasets, tag_type, words, pos, tags):
        pass

    @abc.abstractmethod
    def _transform_to_format(self, sentences_pos_tags, n_tags, word2idx, pos2idx, tag2idx):
        pass

    @abc.abstractmethod
    def _get_data(self, csv_files, tag_type, words, tags):
        pass

    '''
    load the appropriate model (if it exists) depending on if it is a top level or bottom level classifier.
    '''

    @abc.abstractmethod
    def load_model(self, subjects=None, fold=-1):
        pass

    '''
    save the appropriate model (if it exists) depending on if it is a top level or bottom level classifier.
    '''

    @abc.abstractmethod
    def save_model(self, trained_model, subjects=None, fold=-1):
        pass

    @abc.abstractmethod
    def get_model_architecture(self, n_words, n_tags):
        pass

    '''
    Builds dictionary of performance results
    '''

    def _compute_performance(self,learning_type, y_test, y_pred, trained_model, idx2tag, performance_dict=None, filter_class_labels=True):
        if filter_class_labels:
            target_name_indices, target_names = zip(
                *[(idx, tag) for idx, tag in sorted(idx2tag.items(), key=lambda kv: kv[0]) if
                  tag != 'PAD' and tag != 'UNK'])

            precision = metrics.flat_precision_score(
                y_test, y_pred, average='macro', labels=target_name_indices, zero_division=0)
            recall = metrics.flat_recall_score(
                y_test, y_pred, average='macro', labels=target_name_indices, zero_division=0)
            f1 = metrics.flat_f1_score(
                y_test, y_pred, average='macro', labels=target_name_indices, zero_division=0)
            accuracy = metrics.flat_accuracy_score(y_test, y_pred)

            print(
                metrics.flat_classification_report(
                    y_test, y_pred, zero_division=0, target_names=target_names, labels=target_name_indices, digits=2
                )
            )
        else:
            precision = metrics.flat_precision_score(
                y_test, y_pred, average='macro', zero_division=0)
            recall = metrics.flat_recall_score(
                y_test, y_pred, average='macro', zero_division=0)
            f1 = metrics.flat_f1_score(
                y_test, y_pred, average='macro', zero_division=0)
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

        self.all_results[learning_type + '_' + self._name].append(
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
        results = {}
        for metric, value in performance_dict.items():
            results[metric] = value / self._k_cross_validation
            print(metric, results[metric])

    def get_class_weight(self, y, pad_idx=0, unk_idx=1, normalize=False):
        support = Counter(y.flatten())
        del support[pad_idx]
        del support[unk_idx]
        total_classes = len(support)
        total_support = sum(support.values())

        minority_weighted = {curr_class : total_support / (class_support * total_classes)
                             for curr_class,class_support in support.items()}

        if normalize:
            max_class_support = max(minority_weighted.values())
            minority_weighted = {curr_class: class_support / max_class_support for curr_class, class_support in
                             minority_weighted.items()}
        minority_weighted[pad_idx] = 1
        minority_weighted[unk_idx] = 1
        minority_weighted = [curr_class[1] for curr_class in sorted(minority_weighted.items(), key=lambda x: x[0])]

        return minority_weighted

    def get_which_samples(self, y, tag_indices):
        include_sample = {}
        for idx, y_ in enumerate(y):
            include_sample[idx] = False
            for tag_idx in tag_indices:
                if tag_idx in y_:
                    include_sample[idx] = True
                    break
        return include_sample
