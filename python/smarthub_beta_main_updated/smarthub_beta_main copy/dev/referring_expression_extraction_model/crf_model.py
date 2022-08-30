import datetime
import itertools
import pickle
import re
from os import path
import string
from copy import copy
import numpy as np
import pandas as pd
from sklearn_crfsuite import CRF
from sklearn_crfsuite.metrics import \
    flat_classification_report
from sklearn.model_selection import KFold
from .referring_expression_extraction_model import ReferringExpressionExtractionModel
from .utils import LearningTypeConfig
from ..corpus_extractor.corpusannotations.referring_expression_info import ReferringExpressionInfo


class CRFModel(ReferringExpressionExtractionModel):
    def __init__(self):
        super().__init__(name='CRFModel')

    def train(self,
              source_task_csv_files,
              target_task_csv_files=None,
              source_tag_type='RefExp_Tag',
              target_tag_type=None,
              learning_type=LearningTypeConfig.SINGLE_TASK_LEARNING,
              k_cross_validation=5,
              iterations=10,
              embedding_type=None,
              max_seq_len=None,
              batch_size=None,
              evaluate=False,
              embedding_dim=None):

        super().train(
            source_task_csv_files,
            target_task_csv_files,
            source_tag_type,
            target_tag_type,
            learning_type,
            k_cross_validation,
            iterations,
            embedding_type,
            max_seq_len,
            batch_size,
            evaluate,
            embedding_dim)

        source_datasets, source_words, source_tags = self._process_data(source_task_csv_files, source_tag_type)
        n_source_words, n_source_tags = len(source_words), len(source_tags)
        source_tag2idx = {t: i for i, t in enumerate(source_tags)}
        #source_tag2idx['PAD'] = 0
        source_idx2tag = {i: w for w, i in source_tag2idx.items()}

        performance = dict()
        fold = 0
        all_data = self._get_training_data_fn(source_datasets, source_tag_type, None, None)

        for data in all_data:
            train, test, X_train, y_train, X_test, y_test = data[0], data[1], data[2], data[3], data[4], data[5]

            trained_model = self.load_model(subjects=test, fold=fold)
            if trained_model:
                print("Found existing model for X_train", X_train.shape, "y_train", y_train.shape)
            else:
                trained_model = self.get_model_architecture(None, None)
                start_time = datetime.datetime.now()
                print("Training on X", X_train.shape, "Training on y", y_train.shape)
                trained_model.fit(X_train, y_train)
                end_time = datetime.datetime.now()
                print("TIME DURATION", end_time - start_time)

                self.save_model(trained_model=trained_model, subjects=test, fold=fold)

            # if we want to evaluate for current fold the following accoplishes this.
            if evaluate:
                print("Testing on X", X_test.shape, "Testing on y", y_test.shape)

                y_pred = trained_model.predict(X_test)
                #print(flat_classification_report(y_pred, y_test))

                # skip_pad_ignore=False because there is actually no PADDING (this is not a DL model!)
                performance = self._compute_performance( \
                    learning_type='single_task_learning', y_test=y_test, y_pred=y_pred, trained_model=trained_model, \
                    idx2tag=source_idx2tag, performance_dict=performance, filter_class_labels=False)

            fold += 1
            # Now that we trained this model we can yield it for the current fold
            yield trained_model

        if evaluate:
            self._print_performance(fold=fold, performance_dict=performance, name=self._name)

    # Input: Lets see this same graph but for River North"
    # Output: [[('this', 'B-ref', 2, (9, 13)), ('same', 'I-ref', 3, (14, 18)), ('graph', 'I-ref', 4, (19, 24))]]
    def predict(self, trained_model, utterance):
        sentences_pos_tags = [(word.text, word.pos_, None) for word in utterance]
        pred = trained_model.predict(self._transform_to_format([sentences_pos_tags], -1, -1, -1, -1)[0])[0]
        word_pred = [(word, tag) for (word, tag) in zip(utterance, pred) if word.text not in string.punctuation]
        word_pred_cpy = copy(word_pred)
        for idx, (word, tag) in enumerate(word_pred_cpy):
            if (idx-1 < 0 or word_pred_cpy[idx - 1][1] == 'O') and tag == 'I-ref':
                word_pred[idx] = (word, 'B-ref')

        ref_exps = []
        idx = 0
        while idx < len(word_pred):

            referring_expression_info = ReferringExpressionInfo()
            referring_expression_info.rid = None
            referring_expression_info.targets = None
            if word_pred[idx][1] == 'B-ref':
                word_idx, start_char_idx, end_char_idx, word, label = idx, word_pred[idx][0].idx, word_pred[idx][
                    0].idx + len(word_pred[idx][0]), word_pred[idx][0].text, word_pred[idx][1]
                referring_expression_info.add(word_idx, start_char_idx, end_char_idx, word, label)
                idx += 1
                while idx < len(word_pred) and word_pred[idx][1] == 'I-ref':
                    word_idx, start_char_idx, end_char_idx, word, label = idx, word_pred[idx][0].idx, word_pred[idx][
                        0].idx + len(word_pred[idx][0]), word_pred[idx][0].text, word_pred[idx][1]
                    referring_expression_info.add(word_idx, start_char_idx, end_char_idx, word, label)
                    idx += 1
                    if idx >= len(word_pred):
                        break
            else:
                idx += 1

            if referring_expression_info.words:
                ref_exps.append(referring_expression_info)

        return ref_exps

    def _get_train_no_split(self, datasets, tag_type, words, tags):
        # no split so just flatten all the data and return.
        X_per_subject, y_per_subject = self._get_data(datasets, tag_type, words, tags)
        X = np.asarray(list(itertools.chain(*X_per_subject)))
        y = np.asarray(list(itertools.chain(*y_per_subject)))
        return [[None, None, X, y, None, None]]

    def _get_single_train_test_split(self, datasets, tag_type, words, tags):
        # Must split across subject verticals not within subjects. Just need a single split.
        # but n_splits=1 is not allowed so we do the trick of n_splits=2 but return from for-loop after just one iteration.

        X_per_subject, y_per_subject = self._get_data(datasets, tag_type, words, tags)
        k_fold = KFold(n_splits=2, shuffle=True, random_state=7)

        # X_train,y_train,X_test,y_test=[],[],[],[]
        total_subjects = len(datasets)
        X_p, y_p = np.zeros((total_subjects,)), \
                   np.zeros((total_subjects,))

        # indices are split for the 16 subjects, into the two lists, train and test.
        for train, test in k_fold.split(X_p, y_p):
            X_train, y_train = X_per_subject[train], y_per_subject[train]
            X_train = np.asarray(list(itertools.chain(*X_train)))
            y_train = np.asarray(list(itertools.chain(*y_train)))

            X_test, y_test = X_per_subject[test], y_per_subject[test]
            X_test = np.asarray(list(itertools.chain(*X_test)))
            y_test = np.asarray(list(itertools.chain(*y_test)))

            # just a single iteration is all we need.
            return [[train, test, X_train, y_train, X_test, y_test]]

    def _get_cross_validation_train_test_split(self, datasets, tag_type, words, tags):
        # Must split across subject verticals not within subjects. We need self._k_cross_validation total folds in our cross validation.
        X_per_subject, y_per_subject = self._get_data(datasets, tag_type, words, tags)
        k_fold = KFold(n_splits=self._k_cross_validation, shuffle=True, random_state=7)

        total_subjects = len(datasets)
        X_p, y_p = np.zeros((total_subjects,)), \
                   np.zeros((total_subjects,))

        # indices are split for the 16 subjects, into the two lists, train and test.
        for train, test in k_fold.split(X_p, y_p):
            X_train, y_train = X_per_subject[train], y_per_subject[train]
            X_train = np.asarray(list(itertools.chain(*X_train)))
            y_train = np.asarray(list(itertools.chain(*y_train)))

            X_test, y_test = X_per_subject[test], y_per_subject[test]
            X_test = np.asarray(list(itertools.chain(*X_test)))
            y_test = np.asarray(list(itertools.chain(*y_test)))

            # For each fold, we yield our training data. Much better to do this then to store the data in array which takes up RAM!
            yield train, test, X_train, y_train, X_test, y_test

    def _transform_to_format(self, sentences_pos_tags, n_tags, word2idx, pos2idx, tag2idx):
        # Convert each sentence from list of Token to list of word_index
        # norm_sentences=[[re.sub('\d', '0', w[0]) for w in s] for s in sentences_pos_tags.values]

        def word2features(sent, i):
            word = sent[i][0]
            postag = sent[i][1]

            features = {
                'bias': 1.0,
                'word.lower()': word.lower(),
                'word[-3:]': word[-3:],
                'word[-2:]': word[-2:],
                'word.isupper()': word.isupper(),
                'word.istitle()': word.istitle(),
                'word.isdigit()': word.isdigit(),
                'postag': postag,
                'postag[:2]': postag[:2],
            }
            if i > 0:
                word1 = sent[i - 1][0]
                postag1 = sent[i - 1][1]
                features.update({
                    '-1:word.lower()': word1.lower(),
                    '-1:word.istitle()': word1.istitle(),
                    '-1:word.isupper()': word1.isupper(),
                    '-1:postag': postag1,
                    '-1:postag[:2]': postag1[:2],
                })
            else:
                features['BOS'] = True

            if i < len(sent) - 1:
                word1 = sent[i + 1][0]
                postag1 = sent[i + 1][1]
                features.update({
                    '+1:word.lower()': word1.lower(),
                    '+1:word.istitle()': word1.istitle(),
                    '+1:word.isupper()': word1.isupper(),
                    '+1:postag': postag1,
                    '+1:postag[:2]': postag1[:2],
                })
            else:
                features['EOS'] = True

            return features

        def sent2features(sent):
            return [word2features(sent, i) for i in range(len(sent))]

        def sent2labels(sent):
            return [label for token, postag, label in sent]

        def sent2tokens(sent):
            return [token for token, postag, label in sent]

        norm_sentences_pos_tags = [[(re.sub('\d', '0', sents), pos, tags) for sents, pos, tags in t] for t in
                                   sentences_pos_tags]

        X = [sent2features(s) for s in norm_sentences_pos_tags]
        y = [sent2labels(s) for s in norm_sentences_pos_tags]

        return X, y

    def _process_data(self, csv_files, tag_type):
        datasets = []
        for csv_file in csv_files:
            dataset = []
            for group_csv_file in csv_file:
                dataset.append( \
                    pd.read_csv(group_csv_file, sep=',', encoding='latin1').fillna(method='ffill'))

            dataset = pd.concat(dataset, ignore_index=True)
            datasets.append(dataset)
        all_datasets = pd.concat(datasets, ignore_index=True)

        words = list(set(all_datasets["Word"].values))
        words = [re.sub('\d', '0', word) for word in words]
        tags = list(set(all_datasets[tag_type].values))

        return datasets, words, tags

    def _get_data(self, datasets, tag_type, words, tags):
        X_per_subject, y_per_subject = [], []
        for dataset in datasets:
            # Store the (word,pos,tag) list for each sentences in the sentences list
            agg_func = lambda s: [[w, p, t] for w, p, t in \
                                  zip(s["Word"].values.tolist(), s['POS'].values.tolist(), s[tag_type].values.tolist())]
            sentences_pos_tags = dataset.groupby("Sentence #").apply(agg_func)

            X, y = self._transform_to_format(sentences_pos_tags, None, None, None, None)
            X_per_subject.append(X)
            y_per_subject.append(y)

        return np.asarray(X_per_subject), np.asarray(y_per_subject)

    def load_model(self, subjects=None, fold=0):
        if subjects is not None:
            model_path = self._model_base_path + '_'.join([str(s) for s in subjects]) + '_' + self._name + '_' + str(
                fold) + '.pkl'
        else:
            model_path = self._model_base_path + self._name + '_' + str(fold) + '.pkl'

        if path.isfile(model_path):
            print("Loading", model_path)
            return pickle.load(open(model_path, 'rb'))
        return None

    def save_model(self, trained_model, subjects=None, fold=0):
        if subjects is not None:
            model_path = self._model_base_path + '_'.join([str(s) for s in subjects]) + '_' + self._name + '_' + str(
                fold) + '.pkl'
        else:
            model_path = self._model_base_path + self._name + '_' + str(fold) + '.pkl'
        print("Saving", model_path)
        pickle.dump(trained_model, open(model_path, 'wb'))
        return True

    def get_model_architecture(self, words, tags):
        crf = CRF(algorithm='lbfgs',
                  c1=0.1,
                  c2=0.1,
                  max_iterations=self._iterations,
                  all_possible_transitions=False)
        return crf
