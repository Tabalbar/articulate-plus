import itertools
import re
from os import path

import gensim
import keras
import numpy as np
import pandas as pd
from keras.layers import LSTM, Embedding, Dense, TimeDistributed, Bidirectional, Average
from keras.models import Model, Input
from keras.preprocessing.sequence import pad_sequences
from keras.callbacks import EarlyStopping
from keras_contrib.layers.crf import CRF, crf_loss, crf_viterbi_accuracy
from sklearn.model_selection import KFold
from collections import Counter

from .referring_expression_extraction_model import ReferringExpressionExtractionModel
from .sequence_metrics import SequenceMetrics
from .utils import UseEmbeddingConfig, LearningTypeConfig


class BILSTMCRFModel(ReferringExpressionExtractionModel):
    def __init__(self):
        super().__init__(name='BILSTMCRFModel')

    def train(self,
              source_task_csv_files,
              target_task_csv_files=None,
              source_tag_type='NER_Tag',
              target_tag_type=None,
              learning_type=LearningTypeConfig.SINGLE_TASK_LEARNING,
              k_cross_validation=5,
              iterations=10,
              embedding_type=UseEmbeddingConfig.USE_CRIME_EMBEDDING,
              max_seq_len=None,
              batch_size=64,
              evaluate=False,
              embedding_dim=100):
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

        source_datasets, source_words, source_pos, source_tags = self._process_data(source_task_csv_files, source_tag_type)
        n_source_words, n_source_pos, n_source_tags = len(source_words), len(source_pos), len(source_tags)
        source_tag2idx = {t: i + 2 for i, t in enumerate(source_tags)}
        source_tag2idx['PAD'] = 0
        source_tag2idx['UNK'] = 1
        source_idx2tag = {i: w for w, i in source_tag2idx.items()}

        if target_task_csv_files:
            target_datasets, target_words, target_pos, target_tags = self._process_data(target_task_csv_files, target_tag_type)
            n_target_words, n_target_pos, n_target_tags = len(target_words), len(target_pos), len(target_tags)
            target_tag2idx = {t: i + 2 for i, t in enumerate(target_tags)}
            target_tag2idx['PAD'] = 0
            target_tag2idx['UNK'] = 1
            # Vocabulary Key:tag_index -> Value:Label/Tag
            target_idx2tag = {i: w for w, i in target_tag2idx.items()}

        if self._learning_type == LearningTypeConfig.TRANSFER_TASK_LEARNING:
            # First train source task with no cross validation.

            # First we load the larger dataset and train a model on that (no cross validation needed).
            # for data in all_data:
            all_data = self._get_train_no_split(source_datasets, source_tag_type, source_words, source_pos, source_tags)
            data = all_data[0]
            trained_model = self.get_model_architecture(source_words, source_pos, source_tags)

            crf = trained_model.layers[-1]
            trained_model.compile(loss=crf.loss_function, optimizer=keras.optimizers.Adam(lr=1e-2), metrics=[crf.accuracy])
            trained_model.summary()

            train, test, X_train, X_pos_train, y_train, X_test, X_pos_test, y_test = \
                data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7]

            # sample only the data which contains tags other than 'O'
            before_class_distribution = Counter(y_train.flatten())
            required_tag_indices = [idx for idx, tag in source_idx2tag.items() if 'B-' in tag]
            X_train, X_pos_train, y_train = self._get_sample_training_data(
                required_tag_indices=required_tag_indices,
                X_train=X_train,
                X_pos_train=X_pos_train,
                y_train=y_train)
            after_class_distribution = Counter(y_train.flatten())
            print("class distribution percent retained",
                  [(source_idx2tag[idx], v / before_class_distribution[idx])
                   for idx, v in after_class_distribution.items()])

            print("Training on X", X_train.shape, "Training on y", y_train.shape)
            class_weight = self.get_class_weight(y_train, pad_idx=source_tag2idx['PAD'], unk_idx=source_tag2idx['UNK'])
            print("class weights", class_weight)
            print("IDX2TAG", source_idx2tag)
            trained_model.fit(
                [X_train, X_pos_train],
                np.expand_dims(y_train, -1),
                batch_size=self._batch_size,
                epochs=iterations,
                verbose=1,
                class_weight=class_weight,
                callbacks=[SequenceMetrics(source_idx2tag, num_inputs=2), EarlyStopping(monitor='val_f1', patience=10, restore_best_weights=True, mode='max')],
                validation_split=0.2
            )

            performance = dict()
            fold = 0
            all_data = self._get_training_data_fn(target_datasets, target_tag_type, target_words, target_pos, target_tags)

            # For this model trained on large data, now we need to get the output of the BiLSTM (3 layers back: Embedding->Bilstm->TimeDist(Dense)->CRF).
            trained_model = Model(trained_model.input, trained_model.layers[-3].output)

            # Now add a new dense layer after the Bilstm, with random weights normalizd to unit gaussian, followed by new CRF layer with the new label size of 4 for RefExps.
            #X = TimeDistributed(Dense(int(self._embedding_dim/2), activation='relu', kernel_initializer='random_normal'))(trained_model.output)
            X = CRF(n_target_tags + 1, sparse_target=True)(trained_model.output)

            trained_model = Model(trained_model.input, X)
            trained_model.summary()

            old_weights = trained_model.get_weights()
            for data in all_data:
                # reset all weights back to original weights as preparation for next fold of k-cross-validation.
                trained_model.set_weights(old_weights)

                crf = trained_model.layers[-1]
                trained_model.compile(loss=crf.loss_function, optimizer=keras.optimizers.Adam(lr=1e-2), metrics=[crf.accuracy])
                trained_model.summary()

                train, test, X_train, X_pos_train, y_train, X_test, X_pos_test, y_test = \
                    data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7]

                # sample only the data which contains tags other than 'O'
                before_class_distribution = Counter(y_train.flatten())
                required_tag_indices = [idx for idx, tag in target_idx2tag.items() if 'B-' in tag]
                X_train, X_pos_train, y_train = self._get_sample_training_data(
                    required_tag_indices=required_tag_indices,
                    X_train=X_train,
                    X_pos_train=X_pos_train,
                    y_train=y_train)
                after_class_distribution = Counter(y_train.flatten())
                print("class distribution percent retained",
                      [(target_idx2tag[idx], v / before_class_distribution[idx])
                       for idx, v in after_class_distribution.items()])

                print("Training on X", X_train.shape, X_pos_train.shape, "Training on y",
                      np.expand_dims(y_train,-1).shape)
                print("Testing on X", X_test.shape, X_pos_test.shape, "Testing on y", np.expand_dims(y_test,-1).shape)
                print("IDX2TAG", target_idx2tag)
                trained_model.fit(
                    [X_train, X_pos_train],
                    np.expand_dims(y_train, -1),
                    batch_size=self._batch_size,
                    epochs=iterations,
                    verbose=1,
                    class_weight=None,
                    callbacks=[SequenceMetrics(target_idx2tag, num_inputs=2), EarlyStopping(monitor='val_f1', patience=10, restore_best_weights=True, mode='max')],
                    validation_data=([X_test, X_pos_test], np.expand_dims(y_test, -1))
                )

                # if we want to evaluate for current fold the following accoplishes this.
                if evaluate:
                    y_pred = trained_model.predict([X_test, X_pos_test])
                    y_pred = np.argmax(y_pred, axis=-1)
                    performance = self._compute_performance(
                        learning_type='transfer_learning', y_test=y_test, y_pred=y_pred, trained_model=trained_model,
                        idx2tag=target_idx2tag, performance_dict=performance)

                fold += 1
                # Now that we trained this model we can yield it for the current fold. No need to delete it as we simply just update its weights at start of loop.
                yield trained_model

        elif self._learning_type == LearningTypeConfig.MULTI_TASK_LEARNING:
            # First train source task with no cross validation.
            all_data = self._get_train_no_split(source_datasets, source_tag_type, source_words, source_pos, source_tags)

            # First we load the larger dataset and train a model on that (no cross validation needed).
            data = all_data[0]
            trained_model1, trained_model2 = self.get_shared_model_architecture(
                source_words, source_pos, source_tags, target_words, target_pos, target_tags)

            '''
            model1 Layers are Embedding->BiLSTM->Dense->CRF
            model2 Layers are Embedding'->BiLSTM'->Dense'->CRF'

            We want model2 to share the first two layers:
            desired model2 layers are Embedding->BiLSTM->Dense'->CRF'
            '''

            crf = trained_model1.layers[-1]
            trained_model1.compile(loss=crf.loss_function, optimizer=keras.optimizers.Adam(lr=1e-2), metrics=[crf.accuracy])
            trained_model1.summary()

            train, test, X_train, X_pos_train, y_train, X_test, X_pos_test, y_test = \
                data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7]

            # sample only the data which contains tags other than 'O'
            before_class_distribution = Counter(y_train.flatten())
            required_tag_indices = [idx for idx, tag in source_idx2tag.items() if 'B-' in tag]
            X_train, X_pos_train, y_train = self._get_sample_training_data(
                required_tag_indices=required_tag_indices,
                X_train=X_train,
                X_pos_train=X_pos_train,
                y_train=y_train)
            after_class_distribution = Counter(y_train.flatten())
            print("class distribution percent retained",
                  [(source_idx2tag[idx], v / before_class_distribution[idx])
                   for idx, v in after_class_distribution.items()])

            print("Training on X", X_train.shape, X_pos_train.shape, "Training on y", np.expand_dims(y_train,-1).shape)
            class_weight = self.get_class_weight(y_train, pad_idx=source_tag2idx['PAD'], unk_idx=source_tag2idx['UNK'])
            print("class weights", class_weight)
            trained_model1.fit(
                [X_train, X_pos_train],
                np.expand_dims(y_train, -1),
                batch_size=self._batch_size,
                epochs=iterations,
                verbose=1,
                class_weight=class_weight,
                callbacks = [SequenceMetrics(source_idx2tag, num_inputs=2),
                             EarlyStopping(monitor='val_f1', patience=10, restore_best_weights=True, mode='max')],
                validation_split = 0.2
            )

            performance = dict()
            fold = 0
            old_weights = trained_model2.get_weights()
            all_data = self._get_training_data_fn(target_datasets, target_tag_type, target_words, target_pos, target_tags)
            for data in all_data:
                # reset all weights back to original weights as preparation for next fold of k-cross-validation.
                trained_model2.set_weights(old_weights)

                crf = trained_model2.layers[-1]
                trained_model2.compile(loss=crf.loss_function, optimizer=keras.optimizers.Adam(lr=1e-2), metrics=[crf.accuracy])
                trained_model2.summary()

                train, test, X_train, X_pos_train, y_train, X_test, X_pos_test, y_test = \
                    data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7]

                # sample only the data which contains tags other than 'O'
                before_class_distribution = Counter(y_train.flatten())
                required_tag_indices = [idx for idx, tag in target_idx2tag.items() if 'B-' in tag]
                X_train, X_pos_train, y_train = self._get_sample_training_data(
                    required_tag_indices=required_tag_indices,
                    X_train=X_train,
                    X_pos_train=X_pos_train,
                    y_train=y_train)
                after_class_distribution = Counter(y_train.flatten())
                print("class distribution percent retained",
                      [(target_idx2tag[idx], v / before_class_distribution[idx])
                       for idx, v in after_class_distribution.items()])

                print("Training on X", X_train.shape, X_pos_train.shape, "Training on y", np.expand_dims(y_train,-1).shape)
                print("Testing on X", X_test.shape, X_pos_test.shape, "Testing on y", np.expand_dims(y_test,-1).shape)
                print("IDX2TAG", target_idx2tag)
                trained_model2.fit(
                    [X_train, X_pos_train],
                    np.expand_dims(y_train, -1),
                    batch_size=self._batch_size,
                    epochs=iterations,
                    verbose=1,
                    class_weight=None,
                    callbacks=[
                        SequenceMetrics(target_idx2tag, num_inputs=2),
                        EarlyStopping(monitor='val_f1', patience=10, restore_best_weights=True, mode='max')],
                    validation_data=([X_test, X_pos_test], np.expand_dims(y_test, -1))
                )

                # if we want to evaluate for current fold the following accoplishes this.
                if evaluate:
                    y_pred = trained_model2.predict([X_test, X_pos_test])
                    y_pred = np.argmax(y_pred, axis=-1)
                    performance = self._compute_performance(
                        learning_type='multi_task_learning', y_test=y_test, y_pred=y_pred, trained_model=trained_model2,
                        idx2tag=target_idx2tag, performance_dict=performance)

                fold += 1
                # Now that we trained this model we can yield it for the current fold. No need to delete it as we simply just update its weights at start of loop.
                yield trained_model2

        else:
            performance = dict()
            fold = 0
            all_data = self._get_training_data_fn(source_datasets, source_tag_type, source_words, source_pos, source_tags)
            trained_model = self.get_model_architecture(source_words, source_pos, source_tags)
            old_weights = trained_model.get_weights()
            for data in all_data:
                trained_model.set_weights(old_weights)

                crf = trained_model.layers[-1]
                trained_model.compile(
                    loss=crf.loss_function, optimizer=keras.optimizers.Adam(lr=1e-3),
                    metrics=[crf.accuracy])
                trained_model.summary()

                train, test, X_train, X_pos_train, y_train, X_test, X_pos_test, y_test = \
                    data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7]

                # sample only the data which contains tags other than 'O'
                before_class_distribution = Counter(y_train.flatten())
                required_tag_indices = [idx for idx, tag in source_idx2tag.items() if 'B-' in tag]
                X_train, X_pos_train, y_train = self._get_sample_training_data(
                    required_tag_indices=required_tag_indices,
                    X_train=X_train,
                    X_pos_train=X_pos_train,
                    y_train=y_train)
                after_class_distribution = Counter(y_train.flatten())
                print("class distribution percent retained",
                      [(source_idx2tag[idx], v / before_class_distribution[idx])
                       for idx, v in after_class_distribution.items()])

                if self._k_cross_validation != -1:
                    print("Training on X", X_train.shape, X_pos_train.shape, "Training on y", np.expand_dims(y_train, -1).shape)
                    print("Testing on X", X_test.shape, X_pos_test.shape, "Testing on y", np.expand_dims(y_test, -1).shape)
                    print("IDX2TAG", source_idx2tag)
                    print("YTRAIN SAMPLE", y_train[0])

                    trained_model.fit(
                        [X_train, X_pos_train],
                        np.expand_dims(y_train, -1),
                        batch_size=self._batch_size,
                        epochs=iterations,
                        verbose=1,
                        class_weight=None,
                        callbacks=[
                            SequenceMetrics(source_idx2tag, num_inputs=2),
                            EarlyStopping(monitor='val_f1', patience=10, restore_best_weights=True, mode='max')],
                        validation_data=([X_test, X_pos_test], np.expand_dims(y_test, -1))
                    )
                else:
                    print("Training on X", X_train.shape, X_pos_train.shape, "Training on y", np.expand_dims(y_train, -1).shape)
                    print("Testing on X", X_test.shape, X_pos_test.shape, "Testing on y", np.expand_dims(y_test, -1).shape)
                    print("YTRAIN SAMPLE", y_train[0])
                    print("IDX2TAG", source_idx2tag)
                    trained_model.fit(
                        [X_train, X_pos_train],
                        np.expand_dims(y_train, -1),
                        batch_size=self._batch_size,
                        epochs=iterations,
                        verbose=1,
                        class_weight=None,
                        callbacks=[
                            SequenceMetrics(source_idx2tag, num_inputs=2),
                            EarlyStopping(monitor='val_f1', patience=10, restore_best_weights=True, mode='max')],
                        validation_split=0.2
                    )

                # if we want to evaluate for current fold the following accoplishes this.
                if evaluate:
                    y_pred = trained_model.predict([X_test, X_pos_test])
                    y_pred = np.argmax(y_pred, axis=-1)

                    performance = self._compute_performance(
                        learning_type='single_task_learning', y_test=y_test, y_pred=y_pred, trained_model=trained_model,
                        idx2tag=source_idx2tag, performance_dict=performance)

                fold += 1
                # Now that we trained this model we can yield it for the current fold
                yield trained_model

        if evaluate:
            self._print_performance(fold=fold, performance_dict=performance, name=self._name)

    def predict(self, trained_model, utterance):
        pass

    def _get_train_no_split(self, datasets, tag_type, words, pos, tags):
        # no split so just flatten all the data and return.
        X_per_subject, X_pos_per_subject, y_per_subject = self._get_data(datasets, tag_type, words, pos, tags)
        X = np.asarray(list(itertools.chain(*X_per_subject)))
        X_pos = np.asarray(list(itertools.chain(*X_pos_per_subject)))
        y = np.asarray(list(itertools.chain(*y_per_subject)))
        return [[None, None, X, X_pos, y, None, None, None]]

    def _get_single_train_test_split(self, datasets, tag_type, words, pos, tags):
        # Must split across subject verticals not within subjects. Just need a single split.
        # but n_splits=1 is not allowed so we do the trick of n_splits=2 but return from for-loop after just one iteration.

        X_per_subject, X_pos_per_subject, y_per_subject = self._get_data(datasets, tag_type, words, pos, tags)
        k_fold = KFold(n_splits=2, shuffle=True, random_state=7)

        # X_train,y_train,X_test,y_test=[],[],[],[]
        total_subjects = len(datasets)
        X_p, y_p = np.zeros((total_subjects,)), \
                   np.zeros((total_subjects,))

        # indices are split for the 16 subjects, into the two lists, train and test.
        for train, test in k_fold.split(X_p, y_p):
            X_train, X_pos_train, y_train = X_per_subject[train], X_pos_per_subject[train], y_per_subject[train]
            X_train = np.asarray(list(itertools.chain(*X_train)))
            X_pos_train = np.asarray(list(itertools.chain(*X_pos_train)))
            y_train = np.asarray(list(itertools.chain(*y_train)))

            X_test, X_pos_test, y_test = X_per_subject[test], X_pos_per_subject[test], y_per_subject[test]
            X_test = np.asarray(list(itertools.chain(*X_test)))
            X_pos_test = np.asarray(list(itertools.chain(*X_pos_test)))
            y_test = np.asarray(list(itertools.chain(*y_test)))

            # just a single iteration is all we need.
            return [[train, test, X_train, X_pos_train, y_train, X_test, X_pos_test, y_test]]

    def _get_cross_validation_train_test_split(self, datasets, tag_type, words, pos, tags):
        # Must split across subject verticals not within subjects. We need self._k_cross_validation total folds in our cross validation.
        X_per_subject, X_pos_per_subject, y_per_subject = self._get_data(datasets, tag_type, words, pos, tags)
        k_fold = KFold(n_splits=self._k_cross_validation, shuffle=True, random_state=7)

        total_subjects = len(datasets)
        X_p, y_p = np.zeros((total_subjects,)), np.zeros((total_subjects,))

        # indices are split for the 16 subjects, into the two lists, train and test.
        for train, test in k_fold.split(X_p, y_p):
            X_train, X_pos_train, y_train = X_per_subject[train], X_pos_per_subject[train], y_per_subject[train]
            X_train = np.asarray(list(itertools.chain(*X_train)))
            X_pos_train = np.asarray(list(itertools.chain(*X_pos_train)))
            y_train = np.asarray(list(itertools.chain(*y_train)))

            X_test, X_pos_test, y_test = X_per_subject[test], X_pos_per_subject[test], y_per_subject[test]
            X_test = np.asarray(list(itertools.chain(*X_test)))
            X_pos_test = np.asarray(list(itertools.chain(*X_pos_test)))
            y_test = np.asarray(list(itertools.chain(*y_test)))

            # For each fold, we yield our training data. Much better to do this then to store the data in array which takes up RAM!
            yield train, test, X_train, X_pos_train, y_train, X_test, X_pos_test, y_test

    def _transform_to_format(self, sentences_pos_tags, n_tags, word2idx, pos2idx, tag2idx):
        # Convert each sentence from list of Token to list of word_index
        norm_sentences = [[re.sub('\d', '0', w[0]) for w in s] for s in sentences_pos_tags.values]
        X = [[word2idx[w] for w in s] for s in norm_sentences]
        # Padding each sentence to have the same length
        X = pad_sequences(maxlen=self._max_seq_len, sequences=X, padding="post", value=word2idx["PAD"])

        norm_pos = [[p[1] for p in s] for s in sentences_pos_tags.values]
        X_pos = [[pos2idx[p] for p in s] for s in norm_pos]
        X_pos = pad_sequences(maxlen=self._max_seq_len, sequences=X_pos, padding="post", value=pos2idx["PAD"])

        # Convert Tag/Label to tag_index
        y = [[tag2idx[w[2]] for w in s] for s in sentences_pos_tags.values]
        # Padding each sentence to have the same length
        y = pad_sequences(maxlen=self._max_seq_len, sequences=y, padding="post", value=tag2idx["PAD"])
        # One-Hot encode
        #y = [to_categorical(i, num_classes=n_tags + 1) for i in y]  # n_tags+1(PAD)

        return X, X_pos, y

    def _process_data(self, csv_files, tag_type):
        datasets = []
        for csv_file in csv_files:
            dataset = []
            for group_csv_file in csv_file:
                dataset.append(
                    pd.read_csv(group_csv_file, sep=',', encoding='latin1').fillna(method='ffill'))

            dataset = pd.concat(dataset, ignore_index=True)
            datasets.append(dataset)
        all_datasets = pd.concat(datasets, ignore_index=True)

        words = list(set(all_datasets["Word"].values))
        words = [re.sub('\d', '0', word) for word in words]
        pos = list(set(all_datasets["POS"].values))

        tags = list(set(all_datasets[tag_type].values))

        return datasets, words, pos, tags

    def _get_data(self, datasets, tag_type, words, pos, tags):
        # There should be 16 total subjects appended here
        # If we wanted to concatenate the datasets just uncomment line below after the appending line in for-loop below.
        # In our case we cannot do that.
        pad_token = 'PAD'
        unk_token = 'UNK'

        n_words = len(words)
        word2idx = {w: i + 2 for i, w in enumerate(words)}
        word2idx[unk_token] = 1  # Unknown words
        word2idx[pad_token] = 0  # Padding
        # Vocabulary Key:token_index -> Value:word
        idx2word = {i: w for w, i in word2idx.items()}

        tag2idx = {t: i + 2 for i, t in enumerate(tags)}
        tag2idx[unk_token] = 1
        tag2idx[pad_token] = 0

        # Vocabulary Key:tag_index -> Value:Label/Tag
        idx2tag = {i: w for w, i in tag2idx.items()}

        n_tags = len(tags)

        pos2idx = {p: i + 2 for i, p in enumerate(pos)}
        pos2idx[unk_token] = 1
        pos2idx[pad_token] = 0
        idx2pos = {i: p for p, i in pos2idx.items()}

        X_per_subject, X_pos_per_subject, y_per_subject = [], [], []
        for dataset in datasets:
            # Store the (word,pos,tag) list for each sentences in the sentences list
            agg_func = lambda s: [[w, p, t] for w, p, t in \
                                  zip(s["Word"].values.tolist(), s['POS'].values.tolist(), s[tag_type].values.tolist())]
            sentences_pos_tags = dataset.groupby("Sentence #").apply(agg_func)

            X, X_pos, y = self._transform_to_format(sentences_pos_tags, n_tags, word2idx, pos2idx, tag2idx)
            X_per_subject.append(X)
            X_pos_per_subject.append(X_pos)
            y_per_subject.append(y)

        return np.asarray(X_per_subject), np.asarray(X_pos_per_subject), np.asarray(y_per_subject)

    def _get_sample_training_data(self, required_tag_indices, X_train, X_pos_train, y_train):
        include_sample = self.get_which_samples(y=y_train, tag_indices=required_tag_indices)
        X_train, X_pos_train, y_train = zip(
            *[(x, x_pos, y) for idx, (x, x_pos, y) in
              enumerate(zip(X_train, X_pos_train, y_train))
              if include_sample[idx]])
        return np.asarray(X_train), np.asarray(X_pos_train), np.asarray(y_train)

    def load_model(self, subjects=None, fold=0):
        if subjects is not None:
            model_path = self._model_base_path + '_'.join([str(s) for s in subjects]) + '_' + self._name + '_' + str(
                fold) + '.pkl'
        else:
            model_path = self._model_base_path + self._name + '_' + str(fold) + '.pkl'
        if path.isfile(model_path):
            print("Loading", model_path)
            return keras.models.load_model(model_path,
                                           custom_objects={"CRF": CRF, 'crf_loss': crf_loss,
                                                           'crf_viterbi_accuracy': crf_viterbi_accuracy})
        return None

    def save_model(self, trained_model, subjects=None, fold=0):
        if subjects is not None:
            model_path = self._model_base_path + '_'.join([str(s) for s in subjects]) + '_' + self._name + '_' + str(
                fold) + '.pkl'
        else:
            model_path = self._model_base_path + self._name + '_' + str(fold) + '.pkl'
        print("Saving", model_path)
        trained_model.save(model_path)
        return True

    def get_model_architecture(self, words, pos, tags):
        n_words, n_pos, n_tags = len(words), len(pos), len(tags)
        word2idx = {w: i + 2 for i, w in enumerate(words)}

        # input layer
        # input: RE task sentence (MAX_SEQ_LEN, )
        # input: RE task pos (MAX_SEQ_LEN, )
        refexp_sentence = Input(shape=(self._max_seq_len, ))
        refexp_pos = Input(shape=(self._max_seq_len, ))

        # embedding layer
        # input: (BATCH_SIZE X MAX_SEQ_LEN)
        # output: (BATCH_SIZE X MAX_SEQ_LEN X WORD_EMBEDDING_SIZE)
        if self._use_embedding_model:
            embedding_model = gensim.models.KeyedVectors.load(self._embedding_model_path, mmap='r')
            embedding_weights = self._get_embedding_weights_by_index(embedding_model, n_words, word2idx)
            X_refexp_sentence = Embedding(input_dim=n_words + 2, weights=[embedding_weights],
                          output_dim=self._embedding_dim,
                          input_length=self._max_seq_len, mask_zero=True, trainable=True,
                          embeddings_initializer='random_normal')(refexp_sentence)

        else:
            X_refexp_sentence = Embedding(input_dim=n_words + 2, output_dim=self._embedding_dim,
                          input_length=self._max_seq_len, mask_zero=True, trainable=True,
                          embeddings_initializer='random_normal')(refexp_sentence)

        X_refexp_pos = Embedding(input_dim=n_pos + 2, output_dim=self._embedding_dim,
                       input_length=self._max_seq_len, mask_zero=True, trainable=True,
                       embeddings_initializer='random_normal')(refexp_pos)

        # bilstm layer
        # input: (BATCH_SIZE X MAX_SEQ_LEN X WORD_EMBEDDING_SIZE)
        # output: (BATCH_SIZE X MAX_SEQ_LEN X WORD_EMBEDDING_SIZE)
        X_refexp_sentence = Bidirectional(LSTM(units=int(self._embedding_dim/2), return_sequences=True, dropout=0.5,
                               kernel_initializer='random_normal'))(X_refexp_sentence)

        X_refexp_pos = Bidirectional(LSTM(units=int(self._embedding_dim/2), return_sequences=True, dropout=0.5,
                               kernel_initializer='random_normal'))(X_refexp_pos)

        # merge layer
        # input: (BATCH_SIZE X MAX_SEQ_LEN X WORD_EMBEDDING_SIZE)
        # output: (BATCH_SIZE X MAX_SEQ_LEN X WORD_EMBEDDING_SIZE)
        X_refexp = Average()([X_refexp_sentence, X_refexp_pos])

        # dense layer
        # input: (BATCH_SIZE X MAX_SEQ_LEN X WORD_EMBEDDING_SIZE)
        # output: (BATCH_SIZE X MAX_SEQ_LEN X WORD_EMBEDDING_SIZE)
        X_refexp = TimeDistributed(Dense(int(self._embedding_dim/2), activation='relu', kernel_initializer='random_normal'))(X_refexp)

        # crf layer
        # input: (BATCH_SIZE X MAX_SEQ_LEN X 2*WORD_EMBEDDING_SIZE)
        # output: (BATCH_SIZE X MAX_SEQ_LEN X NO_OF_TAGS)
        X_refexp = CRF(n_tags + 1, sparse_target=True)(X_refexp)

        # input [(BATCH_SIZE X MAX_SEQ_LEN), (BATCH_SIZE, MAX_SEQ_LEN)]
        # output (BATCH_SIZE X MAX_SEQ_LEN X NO_OF_TAGS)
        refexp_model = Model(inputs=[refexp_sentence, refexp_pos], output=X_refexp)

        return refexp_model

    '''
    We leverage this for multitask learning. Here we need to create model1 and model2.

    MODEL1  MODEL2
    input1	input2
      \		  /
       \     /
      Embedding
         |
       BiLSTM
        / \
       /   \
      /     \
   Dense   Dense
     |       |
    CRF     CRF

   This method will return [model1, model2]

   Then, the idea in training is:
    model1.fit() on all the "source" data


   old_weights=model1.get_weights() for Embedding and BiLSTM layers (layers 1 and 2)
   For fold in k_cross_folds:
          model2.set_weights(old_weights)

       model2.fit() on all the "target" data

   This sequential approach to multitask learning is a simple way to allow for different batch sizes (i.e., "source" and "target" datasets are different sizes).

    '''

    def get_shared_model_architecture(self, source_words, source_pos, source_tags, target_words, target_pos, target_tags):
        n_source_words, n_source_pos, n_source_tags = len(source_words), len(source_pos), len(source_tags)
        n_target_words, n_target_pos, n_target_tags = len(target_words), len(target_pos), len(target_tags)

        source_word2idx = {w: i + 2 for i, w in enumerate(source_words)}

        # input layer
        # input1: (NER task sentence (MAX_SEQ_LEN, ), NER task pos (MAX_SEQ_LEN, )
        # input2: (RE task sentence (MAX_SEQ_LEN, ), RE task pos (MAX_SEQ_LEN, )
        ner_sentence, ner_pos = Input(shape=(self._max_seq_len,)), Input(shape=(self._max_seq_len,))
        refexp_sentence, refexp_pos = Input(shape=(self._max_seq_len,)), Input(shape=(self._max_seq_len,))

        # embedding layer
        # input: (BATCH_SIZE X MAX_SEQ_LEN)
        # output: (BATCH_SIZE X MAX_SEQ_LEN X WORD_EMBEDDING_SIZE)
        if self._use_embedding_model:
            embedding_model = gensim.models.KeyedVectors.load(self._embedding_model_path, mmap='r')
            embedding_weights = self._get_embedding_weights_by_index(embedding_model, n_source_words, source_word2idx)
            shared_sentence_embedding_layer = Embedding(input_dim=n_source_words + 2, weights=[embedding_weights],
                                               output_dim=self._embedding_dim,
                                               input_length=self._max_seq_len, mask_zero=True, trainable=True,
                                               embeddings_initializer='random_normal')

        else:
            shared_sentence_embedding_layer = Embedding(input_dim=n_source_words + 2, output_dim=self._embedding_dim,
                                               input_length=self._max_seq_len, mask_zero=True, trainable=True,
                                               embeddings_initializer='random_normal')

        X_ner_sentence = shared_sentence_embedding_layer(ner_sentence)
        X_refexp_sentence = shared_sentence_embedding_layer(refexp_sentence)

        shared_pos_embedding_layer = Embedding(input_dim=n_source_pos + 2, output_dim=self._embedding_dim,
                                           input_length=self._max_seq_len, mask_zero=True, trainable=True,
                                           embeddings_initializer='random_normal')

        X_ner_pos = shared_pos_embedding_layer(ner_pos)
        X_refexp_pos = shared_pos_embedding_layer(refexp_pos)

        # bilstm layer
        # input: (BATCH_SIZE X MAX_SEQ_LEN X WORD_EMBEDDING_SIZE)
        # output: (BATCH_SIZE X MAX_SEQ_LEN X WORD_EMBEDDING_SIZE)
        shared_sentence_bilstm_layer = Bidirectional(LSTM(units=int(self._embedding_dim / 2), return_sequences=True, dropout=0.5,
                                                 kernel_initializer='random_normal'))

        X_ner_sentence = shared_sentence_bilstm_layer(X_ner_sentence)
        X_refexp_sentence = shared_sentence_bilstm_layer(X_refexp_sentence)

        shared_pos_bilstm_layer = Bidirectional(LSTM(units=int(self._embedding_dim / 2), return_sequences=True, dropout=0.5,
                                                 kernel_initializer='random_normal'))

        # input: (BATCH_SIZE X MAX_SEQ_LEN X WORD_EMBEDDING_SIZE)
        # output: (BATCH_SIZE X MAX_SEQ_LEN X WORD_EMBEDDING_SIZE)
        X_ner_pos = shared_pos_bilstm_layer(X_ner_pos)
        X_refexp_pos = shared_pos_bilstm_layer(X_refexp_pos)

        # merge layer
        # input: (BATCH_SIZE X MAX_SEQ_LEN X WORD_EMBEDDING_SIZE)
        # output: (BATCH_SIZE X MAX_SEQ_LEN X WORD_EMBEDDING_SIZE)
        X_ner = Average()([X_ner_sentence, X_ner_pos])
        X_refexp = Average()([X_refexp_sentence, X_refexp_pos])

        # crf layer
        # input: (BATCH_SIZE X MAX_SEQ_LEN X WORD_EMBEDDING_SIZE/2)
        # output: (BATCH_SIZE X MAX_SEQ_LEN X NO_OF_TAGS)
        X_ner = CRF(n_source_tags + 1, sparse_target=True)(X_ner)
        X_refexp = CRF(n_target_tags + 1, sparse_target=True)(X_refexp)

        # input to model ([BATCH_SIZE X MAX_SEQ_LEN, BATCH_SIZE X MAX_SEQ_LEN])
        # output from model (BATCH_SIZE X MAX_SEQ_LEN X NO_OF_TAGS)
        ner_model = Model([ner_sentence, ner_pos], X_ner)
        refexp_model = Model([refexp_sentence, refexp_pos], X_refexp)

        return ner_model, refexp_model

    def _get_embedding_weights_by_index(self, embedding_model, n_words, word2idx):
        embedding_weights = np.zeros((n_words + 2, self._embedding_dim))
        for word, idx in word2idx.items():
            if word in embedding_model.wv.vocab:
                embedding_weights[idx] = embedding_model.wv[word]
            else:
                phrase = word.split()

                if len(phrase) < 2:
                    embedding_weights[idx] = np.zeros((self._embedding_dim,))
                else:
                    phrase_lst = []
                    for phrase_word in phrase:
                        if phrase_word in embedding_model.wv.vocab:
                            phrase_lst.append(embedding_model.wv[phrase_word])
                        else:
                            phrase_lst.append(np.zeros((self._embedding_dim,)))
                    embedding_weights[idx] = np.mean(phrase_lst, axis=0)
        return embedding_weights
