import itertools
import os
import re
from os import path

import keras
import keras_bert
import numpy as np
import pandas as pd
from keras.layers import LSTM, Embedding, Dense, TimeDistributed, Bidirectional, Average, Masking
from keras.callbacks import EarlyStopping
from keras.models import Model, Input
from keras_contrib.layers import CRF
from sklearn.model_selection import KFold
from collections import Counter

from .referring_expression_extraction_model import ReferringExpressionExtractionModel
from .sequence_metrics import SequenceMetrics
from .utils import UseEmbeddingConfig, LearningTypeConfig


class BERTCRFModel(ReferringExpressionExtractionModel):
    def __init__(self):
        super().__init__(name='BERTCRFModel')
        BERT_MODEL_DIR = '../bert_models/'
        BERT_MODEL_NAME = 'cased_L-12_H-768_A-12/'

        self._BERT_CHECKPOINT_DIR = os.path.join(BERT_MODEL_DIR, BERT_MODEL_NAME)
        self._BERT_CHECKPOINT_FILE = os.path.join(self._BERT_CHECKPOINT_DIR, "bert_model.ckpt")
        self._BERT_CONFIG_FILE = os.path.join(self._BERT_CHECKPOINT_DIR, "bert_config.json")
        self._BERT_VOCAB_FILE = os.path.join(self._BERT_CHECKPOINT_DIR, "vocab.txt")

        token_dict = keras_bert.load_vocabulary(self._BERT_VOCAB_FILE)
        self._tokenizer = keras_bert.Tokenizer(token_dict=token_dict, cased=True)

    def train(self,
              source_task_csv_files,
              target_task_csv_files=None,
              source_tag_type='NER_Tag',
              target_tag_type=None,
              learning_type=LearningTypeConfig.SINGLE_TASK_LEARNING,
              k_cross_validation=5,
              iterations=5,
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
            all_data = self._get_train_no_split(source_datasets, source_tag_type, source_words, source_pos, source_tags)
            data = all_data[0]
            condensed_trained_model, trained_model = self.get_model_architecture(source_words, source_pos, source_tags)

            crf = trained_model.layers[-1]
            trained_model.compile(loss=crf.loss_function, optimizer=keras.optimizers.Adam(lr=1e-1), metrics=[crf.accuracy])
            trained_model.summary()

            (X_train_sentences, X_train_segment_ids, X_train_mask_ids), \
            X_pos_train, \
            y_train, \
            (X_test_sentences, X_test_segment_ids, X_test_mask_ids), \
            X_pos_test, \
            y_test = data[0], data[1], data[2], data[3], data[4], data[5]

            # sample only the data which contains tags other than 'O'
            required_tag_indices = [idx for idx, tag in source_idx2tag.items() if 'B-' in tag]
            X_train_sentences, X_train_segment_ids, X_train_mask_ids, X_pos_train, y_train = self._get_sample_training_data(
                required_tag_indices=required_tag_indices,
                X_train_sentences=X_train_sentences,
                X_train_segment_ids=X_train_segment_ids,
                X_train_mask_ids=X_train_mask_ids,
                X_pos_train=X_pos_train,
                y_train=y_train)

            print("Training on X", X_train_sentences.shape, "Training on y", np.expand_dims(y_train, -1).shape)
            class_weight = self.get_class_weight(y_train, pad_idx=source_tag2idx['PAD'], unk_idx=source_tag2idx['UNK'])
            print("class weights", class_weight)
            print("IDX2TAG", source_idx2tag)

            trained_model.fit(
                [X_train_sentences, X_train_segment_ids, X_train_mask_ids, X_pos_train],
                np.expand_dims(y_train, -1),
                batch_size=self._batch_size,
                epochs=iterations,
                verbose=1,
                class_weight=class_weight,
                callbacks=[SequenceMetrics(source_idx2tag), EarlyStopping(monitor='val_f1', patience=10, restore_best_weights=True, mode='max')],
                validation_split=0.2
            )

            # For this model trained on large data, now we need to get the output of the BERT (10 layers back: InputLayer->InputLayer->InputLayer->Bert Model->TimeDist(Dense)->TimeDist(Dense)->CRF).
            trained_model = Model(trained_model.inputs, trained_model.layers[-3].output)

            # Now add a new dense layer after BERT, with random weights normalizd to unit gaussian, followed by new CRF layer with the new label size of 4 for RefExps.
            X = TimeDistributed(Dense(int(self._embedding_dim/2), activation='relu', kernel_initializer='random_normal'))(trained_model.output)
            X = CRF(n_target_tags + 1, sparse_target=True)(X)

            trained_model = Model(trained_model.input, X)
            trained_model.summary()

            performance = dict()
            fold = 0
            all_data = self._get_training_data_fn(target_datasets, target_tag_type, target_words, target_pos, target_tags)
            old_weights = trained_model.get_weights()
            for data in all_data:
                # reset all weights back to original weights as preparation for next fold of k-cross-validation.
                trained_model.set_weights(old_weights)

                crf = trained_model.layers[-1]
                trained_model.compile(
                    loss=crf.loss_function, optimizer=keras.optimizers.Adam(lr=1e-1), metrics=[crf.accuracy]
                )

                (X_train_sentences, X_train_segment_ids, X_train_mask_ids), \
                X_pos_train, \
                y_train, \
                (X_test_sentences, X_test_segment_ids, X_test_mask_ids), \
                X_pos_test, \
                y_test = data[0], data[1], data[2], data[3], data[4], data[5]

                # sample only the data which contains tags other than 'O'
                required_tag_indices = [idx for idx, tag in target_idx2tag.items() if 'B-' in tag]
                X_train_sentences, X_train_segment_ids, X_train_mask_ids, X_pos_train, y_train = \
                    self._get_sample_training_data(
                        required_tag_indices=required_tag_indices,
                        X_train_sentences=X_train_sentences,
                        X_train_segment_ids=X_train_segment_ids,
                        X_train_mask_ids=X_train_mask_ids,
                        X_pos_train=X_pos_train,
                        y_train=y_train
                    )

                print(
                    "Training on X", X_train_sentences.shape, X_pos_train.shape,
                    "Training on y", np.expand_dims(y_train, -1).shape, Counter(y_train.flatten()))
                print("Testing on X", X_test_sentences.shape, X_pos_test.shape,
                      "Training on y", np.expand_dims(y_test, -1).shape, Counter(y_test.flatten()))
                print("IDX2TAG", target_idx2tag)

                trained_model.fit(
                    [X_train_sentences, X_train_segment_ids, X_train_mask_ids, X_pos_train],
                    np.expand_dims(y_train, -1),
                    batch_size=self._batch_size,
                    epochs=iterations,
                    verbose=1,
                    class_weight=None,
                    callbacks=[
                        SequenceMetrics(target_idx2tag),
                        EarlyStopping(monitor='val_f1', patience=10, restore_best_weights=True, mode='max')],
                    validation_data=(
                        [X_test_sentences, X_test_segment_ids, X_test_mask_ids, X_pos_test],
                        np.expand_dims(y_test, -1))
            )

                # if we want to evaluate for current fold the following accoplishes this.
                if evaluate:
                    y_pred = trained_model.predict([X_test_sentences, X_test_segment_ids, X_test_mask_ids, X_pos_test])

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
            trained_model1.compile(
                loss=crf.loss_function, optimizer=keras.optimizers.Adam(lr=1e-1), metrics=[crf.accuracy])
            trained_model1.summary()

            (X_train_sentences, X_train_segment_ids, X_train_mask_ids), \
            X_pos_train, \
            y_train, \
            (X_test_sentences, X_test_segment_ids, X_test_mask_ids), \
            X_pos_test, \
            y_test = data[0], data[1], data[2], data[3], data[4], data[5]

            # sample only the data which contains tags other than 'O'
            required_tag_indices = [idx for idx,tag in source_idx2tag.items() if 'B-' in tag]
            X_train_sentences, X_train_segment_ids, X_train_mask_ids, X_pos_train, y_train = self._get_sample_training_data(
                required_tag_indices=required_tag_indices,
                X_train_sentences=X_train_sentences,
                X_train_segment_ids=X_train_segment_ids,
                X_train_mask_ids=X_train_mask_ids,
                X_pos_train=X_pos_train,
                y_train=y_train)

            print("Training on X", X_train_sentences.shape, X_pos_train.shape, "Training on y", y_train.shape)
            class_weight = self.get_class_weight(y_train, pad_idx=source_tag2idx['PAD'], unk_idx=source_tag2idx['UNK'])
            print("class weights", class_weight)
            print("IDX2TAG", source_idx2tag)
            trained_model1.fit(
                [X_train_sentences, X_train_segment_ids, X_train_mask_ids, X_pos_train],
                np.expand_dims(y_train, -1),
                batch_size=self._batch_size,
                epochs=iterations,
                verbose=1,
                class_weight=class_weight,
                callbacks=[
                    SequenceMetrics(source_idx2tag),
                    EarlyStopping(monitor='val_f1', patience=10, restore_best_weights=True, mode='max')
                ],
                validation_split=0.2
            )

            performance = dict()
            fold = 0
            old_weights = trained_model2.get_weights()
            all_data = self._get_training_data_fn(target_datasets, target_tag_type, target_words, target_pos, target_tags)
            for data in all_data:
                # reset all weights back to original weights as preparation for next fold of k-cross-validation.
                trained_model2.set_weights(old_weights)

                crf = trained_model2.layers[-1]
                trained_model2.compile(
                    loss=crf.loss_function, optimizer=keras.optimizers.Adam(lr=1e-1), metrics=[crf.accuracy])
                trained_model2.summary()

                (X_train_sentences, X_train_segment_ids, X_train_mask_ids), \
                X_pos_train, \
                y_train, \
                (X_test_sentences, X_test_segment_ids, X_test_mask_ids), \
                X_pos_test, \
                y_test = data[0], data[1], data[2], data[3], data[4], data[5]

                # sample only the data which contains tags other than 'O'
                required_tag_indices = [idx for idx, tag in target_idx2tag.items() if 'B-' in tag]
                X_train_sentences, X_train_segment_ids, X_train_mask_ids, X_pos_train, y_train = \
                    self._get_sample_training_data(
                        required_tag_indices=required_tag_indices,
                        X_train_sentences=X_train_sentences,
                        X_train_segment_ids=X_train_segment_ids,
                        X_train_mask_ids=X_train_mask_ids,
                        X_pos_train=X_pos_train,
                        y_train=y_train
                    )

                print("Training on X", X_train_sentences.shape, "Training on y", y_train.shape)
                print("class weights", class_weight)
                print("IDX2TAG", target_idx2tag)
                trained_model2.fit(
                    [X_train_sentences, X_train_segment_ids, X_train_mask_ids, X_pos_train],
                    np.expand_dims(y_train, -1),
                    batch_size=self._batch_size,
                    epochs=iterations,
                    verbose=1,
                    class_weight=None,
                    callbacks=[SequenceMetrics(target_idx2tag),
                               EarlyStopping(monitor='val_f1', patience=10, restore_best_weights=True, mode='max')],
                    validation_data=(
                    [X_test_sentences, X_test_segment_ids, X_test_mask_ids, X_pos_test], np.expand_dims(y_test, -1))
                )

                # if we want to evaluate for current fold the following accoplishes this.
                if evaluate:
                    y_pred = trained_model2.predict([X_test_sentences, X_test_segment_ids, X_test_mask_ids, X_pos_test])
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
            condensed_trained_model, trained_model = self.get_model_architecture(source_words, source_pos, source_tags)

            for i, l in enumerate(trained_model.layers):
                print(f'layer {i}: {l}')
                try:
                    print(f'has input mask: {l.input_mask}')
                    print(f'has output mask: {l.output_mask}')
                except:
                    print("Failed")
                    continue

            old_weights = trained_model.get_weights()
            for data in all_data:
                trained_model.set_weights(old_weights)

                crf = trained_model.layers[-1]
                trained_model.compile(loss=crf.loss_function, optimizer=keras.optimizers.Adam(lr=1e-3), metrics=[crf.accuracy])
                trained_model.summary()

                (X_train_sentences, X_train_segment_ids, X_train_mask_ids), \
                X_pos_train, \
                y_train, \
                (X_test_sentences, X_test_segment_ids, X_test_mask_ids), \
                X_pos_test, \
                y_test = data[0], data[1], data[2], data[3], data[4], data[5]

                required_tag_indices = [idx for idx, tag in source_idx2tag.items() if 'B-' in tag]
                X_train_sentences, X_train_segment_ids, X_train_mask_ids, X_pos_train, y_train = self._get_sample_training_data(
                    required_tag_indices=required_tag_indices,
                    X_train_sentences=X_train_sentences,
                    X_train_segment_ids=X_train_segment_ids,
                    X_train_mask_ids=X_train_mask_ids,
                    X_pos_train=X_pos_train,
                    y_train=y_train)

                if self._k_cross_validation != -1:
                    # sample only the data which contains tags other than 'O'
                    print("Training on X", X_train_sentences.shape, X_pos_train.shape, "Training on y", y_train.shape, "norm",
                          np.expand_dims(y_train, -1).shape, Counter(y_train.flatten()))
                    print("Testing on X", X_train_sentences.shape, X_pos_test.shape, "Training on y", y_train.shape, "norm",
                          np.expand_dims(y_test, -1).shape, Counter(y_test.flatten()))
                    print("IDX2TAG", source_idx2tag)

                    trained_model.fit(
                        [X_train_sentences, X_train_segment_ids, X_train_mask_ids, X_pos_train],
                        np.expand_dims(y_train, -1),
                        batch_size=self._batch_size,
                        epochs=iterations,
                        verbose=1,
                        class_weight=None,
                        callbacks=[SequenceMetrics(source_idx2tag),
                                   EarlyStopping(monitor='val_f1', patience=10, restore_best_weights=True, mode='max')],
                        validation_data=(
                            [X_test_sentences, X_test_segment_ids, X_test_mask_ids, X_pos_test],
                            np.expand_dims(y_test, -1)
                        )
                    )
                else:
                    print("Training on X", X_train_sentences.shape, X_pos_train.shape, "Training on y", y_train.shape)
                    print("Testing on X", X_test_sentences.shape, X_pos_test.shape, "Training on y", y_train.shape)
                    print("IDX2TAG", source_idx2tag)
                    trained_model.fit(
                        [X_train_sentences, X_train_segment_ids, X_train_mask_ids, X_pos_train],
                        np.expand_dims(y_train, -1),
                        batch_size=self._batch_size,
                        epochs=iterations,
                        verbose=1,
                        class_weight=None,
                        callbacks=[SequenceMetrics(source_idx2tag),
                                   EarlyStopping(monitor='val_f1', patience=20, restore_best_weights=True, mode='max')],
                        validation_split=0.2
                    )

                # if we want to evaluate for current fold the following accoplishes this.
                if evaluate:
                    y_pred = trained_model.predict([X_test_sentences, X_test_segment_ids, X_test_mask_ids, X_pos_test])
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

        X_sentences = [sentences for (sentences, segment_ids, mask_ids) in [subject for subject in X_per_subject]]
        X_sentences = np.asarray(list(itertools.chain(*X_sentences)))

        X_segment_ids = [segment_ids for (sentences, segment_ids, mask_ids) in [subject for subject in X_per_subject]]
        X_segment_ids = np.asarray(list(itertools.chain(*X_segment_ids)))

        X_mask_ids = [mask_ids for (sentences, segment_ids, mask_ids) in [subject for subject in X_per_subject]]
        X_mask_ids = np.asarray(list(itertools.chain(*X_mask_ids)))

        X_pos = np.asarray(list(itertools.chain(*X_pos_per_subject)))

        y = np.asarray(list(itertools.chain(*y_per_subject)))

        return [[(X_sentences, X_segment_ids, X_mask_ids), X_pos, y, (None, None, None), None, None]]

    def _get_single_train_test_split(self, datasets, tag_type, words, pos, tags):
        # Must split across subject verticals not within subjects. We need self._k_cross_validation total folds in our cross validation.
        X_per_subject, X_pos_per_subject, y_per_subject = self._get_data(datasets, tag_type, words, pos, tags)
        k_fold = KFold(n_splits=self._k_cross_validation, shuffle=True, random_state=7)

        total_subjects = len(datasets)
        X_p, y_p = np.zeros((total_subjects,)), np.zeros((total_subjects,))

        # indices are split for the 16 subjects, into the two lists, train and test.
        for train, test in k_fold.split(X_p, y_p):
            X_train, X_pos_train, y_train = X_per_subject[train], X_pos_per_subject[train], y_per_subject[train]
            X_train_sentences = [np.asarray(sentences, dtype='int32') for (sentences, segment_ids, mask_ids) in
                                 [subject for subject in X_train]]
            X_train_sentences = np.asarray(list(itertools.chain(*X_train_sentences)))
            X_train_segment_ids = [np.asarray(segment_ids, dtype='int32') for (sentences, segment_ids, mask_ids) in
                                   [subject for subject in X_train]]
            X_train_segment_ids = np.asarray(list(itertools.chain(*X_train_segment_ids)))
            X_train_mask_ids = [np.asarray(mask_ids, dtype='int32') for (sentences, segment_ids, mask_ids) in
                                [subject for subject in X_train]]
            X_train_mask_ids = np.asarray(list(itertools.chain(*X_train_mask_ids)))
            X_pos_train = np.asarray(list(itertools.chain(*X_pos_train)))
            y_train = np.asarray(list(itertools.chain(*y_train)))

            X_test, X_pos_test, y_test = X_per_subject[test], X_pos_per_subject[test], y_per_subject[test]
            X_test_sentences = [np.asarray(sentences, dtype='int32') for (sentences, segment_ids, mask_ids) in
                                [subject for subject in X_test]]
            X_test_sentences = np.asarray(list(itertools.chain(*X_test_sentences)))
            X_test_segment_ids = [np.asarray(segment_ids, dtype='int32') for (sentences, segment_ids, mask_ids) in
                                  [subject for subject in X_test]]
            X_test_segment_ids = np.asarray(list(itertools.chain(*X_test_segment_ids)))
            X_test_mask_ids = [np.asarray(mask_ids, dtype='int32') for (sentences, segment_ids, mask_ids) in
                               [subject for subject in X_test]]
            X_test_mask_ids = np.asarray(list(itertools.chain(*X_test_mask_ids)))
            X_pos_test = np.asarray(list(itertools.chain(*X_pos_test)))
            y_test = np.asarray(list(itertools.chain(*y_test)))

            # For each fold, we yield our training data. Much better to do this then to store the data in array which takes up RAM!
            return \
                [(np.asarray(X_train_sentences),
                  np.asarray(X_train_segment_ids),
                  np.asarray(X_train_mask_ids)),
                 X_pos_train,
                 y_train,
                 (np.asarray(X_test_sentences),
                  np.asarray(X_test_segment_ids),
                  np.asarray(X_test_mask_ids)),
                 X_pos_test,
                 y_test]

    def _get_cross_validation_train_test_split(self, datasets, tag_type, words, pos, tags):
        # Must split across subject verticals not within subjects. We need self._k_cross_validation total folds in our cross validation.
        X_per_subject, X_pos_per_subject, y_per_subject = self._get_data(datasets, tag_type, words, pos, tags)
        k_fold = KFold(n_splits=self._k_cross_validation, shuffle=True, random_state=7)

        total_subjects = len(datasets)
        X_p, y_p = np.zeros((total_subjects,)), np.zeros((total_subjects,))

        # indices are split for the 16 subjects, into the two lists, train and test.
        for train, test in k_fold.split(X_p, y_p):
            X_train, X_pos_train, y_train = X_per_subject[train], X_pos_per_subject[train], y_per_subject[train]
            X_train_sentences = [np.asarray(sentences, dtype='int32') for (sentences, segment_ids, mask_ids) in
                                 [subject for subject in X_train]]
            X_train_sentences = np.asarray(list(itertools.chain(*X_train_sentences)))
            X_train_segment_ids = [np.asarray(segment_ids, dtype='int32') for (sentences, segment_ids, mask_ids) in
                                   [subject for subject in X_train]]
            X_train_segment_ids = np.asarray(list(itertools.chain(*X_train_segment_ids)))
            X_train_mask_ids = [np.asarray(mask_ids, dtype='int32') for (sentences, segment_ids, mask_ids) in
                                [subject for subject in X_train]]
            X_train_mask_ids = np.asarray(list(itertools.chain(*X_train_mask_ids)))
            X_pos_train = np.asarray(list(itertools.chain(*X_pos_train)))
            y_train = np.asarray(list(itertools.chain(*y_train)))

            X_test, X_pos_test, y_test = X_per_subject[test], X_pos_per_subject[test], y_per_subject[test]
            X_test_sentences = [np.asarray(sentences, dtype='int32') for (sentences, segment_ids, mask_ids) in
                                [subject for subject in X_test]]
            X_test_sentences = np.asarray(list(itertools.chain(*X_test_sentences)))
            X_test_segment_ids = [np.asarray(segment_ids, dtype='int32') for (sentences, segment_ids, mask_ids) in
                                  [subject for subject in X_test]]
            X_test_segment_ids = np.asarray(list(itertools.chain(*X_test_segment_ids)))
            X_test_mask_ids = [np.asarray(mask_ids, dtype='int32') for (sentences, segment_ids, mask_ids) in
                               [subject for subject in X_test]]
            X_test_mask_ids = np.asarray(list(itertools.chain(*X_test_mask_ids)))
            X_pos_test = np.asarray(list(itertools.chain(*X_pos_test)))
            y_test = np.asarray(list(itertools.chain(*y_test)))

            # For each fold, we yield our training data. Much better to do this then to store the data in array which takes up RAM!
            yield \
                (np.asarray(X_train_sentences),
                 np.asarray(X_train_segment_ids),
                 np.asarray(X_train_mask_ids)), \
                X_pos_train, \
                y_train, \
                (np.asarray(X_test_sentences),
                 np.asarray(X_test_segment_ids),
                 np.asarray(X_test_mask_ids)), \
                X_pos_test, \
                y_test

    def _transform_to_format(self, sentences_pos_tags, n_tags, word2idx, pos2idx, tag2idx):
        input_ids_list = []
        input_masks_list = []
        segment_ids_list = []
        label_id_list = []
        pos_id_list = []

        pad_token_label_id = tag2idx['PAD']
        pad_token_pos_id = pos2idx['PAD']
        for idx, words_pos_tags in enumerate(sentences_pos_tags):
            tokens = []
            pos_ids = []
            label_ids = []

            for word, pos, tag in words_pos_tags:
                word_tokens = self._tokenizer.tokenize(word)[1:-1]
                if not word_tokens:
                    word_tokens = "'"
                tokens.extend(word_tokens)
                # Use the real label id for the first token of the word, and
                # padding ids for the remaining tokens
                label_ids.extend([tag2idx[tag]] + [pad_token_label_id] * (len(word_tokens) - 1))
                pos_ids.extend([pos2idx[pos]] + [pad_token_pos_id] * (len(word_tokens) - 1))

            # Make 2 spaces available so that we can add [CLS] and [SEP]
            tokens = [t.strip() for t in tokens]
            tokens = tokens[: (self._max_seq_len - 2)]
            tokens = ['[CLS]'] + tokens + ['[SEP]']

            label_ids = label_ids[: (self._max_seq_len - 2)]
            label_ids = [pad_token_label_id] + label_ids + [pad_token_label_id]
            pos_ids = pos_ids[: (self._max_seq_len - 2)]
            pos_ids = [pad_token_pos_id] + pos_ids + [pad_token_pos_id]

            # Add padding.
            no_of_pads = self._max_seq_len - len(tokens)

            input_masks_list.append([1] * len(tokens) + [0] * no_of_pads)

            tokens += ['[PAD]'] * no_of_pads

            label_ids += [pad_token_label_id] * no_of_pads
            pos_ids += [pad_token_pos_id] * no_of_pads

            input_ids = self._tokenizer._convert_tokens_to_ids(tokens)
            input_ids_list.append(input_ids)

            segment_ids_list.append([0] * len(tokens))

            label_id_list.append(label_ids)
            pos_id_list.append(pos_ids)

        return np.asarray(input_ids_list, dtype='int32'), \
               np.asarray(segment_ids_list, dtype='int32'), \
               np.asarray(input_masks_list, dtype='int32'), \
               np.asarray(pos_id_list), \
               np.array([np.array(x) for x in label_id_list])

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

        n_tags = len(tag2idx.keys())

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

            X, segment_ids, input_masks, X_pos, y = self._transform_to_format(sentences_pos_tags, n_tags, word2idx, pos2idx, tag2idx)
            X_per_subject.append((X, segment_ids, input_masks))
            X_pos_per_subject.append(X_pos)
            y_per_subject.append(y)
        return np.asarray(X_per_subject), np.asarray(X_pos_per_subject), np.asarray(y_per_subject)

    def _get_sample_training_data(self, required_tag_indices, X_train_sentences, X_train_segment_ids, X_train_mask_ids, X_pos_train, y_train):
        include_sample = self.get_which_samples(y=y_train, tag_indices=required_tag_indices)
        X_train_sentences, X_train_segment_ids, X_train_mask_ids, X_pos_train, y_train = zip(
            *[(x, x_seg, x_mask, x_pos, y) for idx, (x, x_seg, x_mask, x_pos, y) in
              enumerate(zip(X_train_sentences, X_train_segment_ids, X_train_mask_ids, X_pos_train, y_train))
              if include_sample[idx]])
        return np.asarray(
            X_train_sentences), np.asarray(X_train_segment_ids), np.asarray(X_train_mask_ids), np.asarray(X_pos_train), np.asarray(y_train)

    def load_model(self, subjects=None, fold=0):
        if subjects is not None:
            model_path = self._model_base_path + '_'.join([str(s) for s in subjects]) + '_' + self._name + '_' + str(
                fold) + '.pkl'
        else:
            model_path = self._model_base_path + self._name + '_' + str(fold) + '.pkl'
        if path.isfile(model_path):
            print("Loading", model_path)
            return keras.models.load_model(model_path)
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

    def _create_bert_keras_model(self):
        layerN = 12
        # bert_params = bert.params_from_pretrained_ckpt(self._BERT_CHECKPOINT_DIR)
        # bert_layer = bert.BertModelLayer.from_params(bert_params, name="bert")
        # bert_layer.apply_adapter_freeze()
        bert_model = keras_bert.load_trained_model_from_checkpoint(
            self._BERT_CONFIG_FILE,
            self._BERT_CHECKPOINT_FILE,
            seq_len=self._max_seq_len,
            training=True,
            trainable=False
            # trainable=['Encoder-{}-MultiHeadSelfAttention-Adapter'.format(i+1) for i in range(layerN)]+
            # ['Encoder-{}-FeedForward-Adapter'.format(i+1) for i in range(layerN)]+
            # ['Encoder-{}-MultiHeadSelfAttention-Norm'.format(i+1) for i in range(layerN)]+
            # ['Encoder-{}-FeedForward-Norm'.format(i+1) for i in range(layerN)]
        )
        return bert_model

    def get_model_architecture(self, words, pos, tags):
        n_words, n_pos, n_tags = len(words), len(pos), len(tags)
        word2idx = {w: i + 2 for i, w in enumerate(words)}

        bert_model = self._create_bert_keras_model()
        X_bert = bert_model.get_layer(index=-9).output
        updated_bert_model = Model(inputs=bert_model.input, outputs=X_bert)

        # input layer
        # input: RE task sentence [(MAX_SEQ_LEN, ), (MAX_SEQ_LEN, )]
        # input: RE task pos (MAX_SEQ_LEN, )
        input_ids = Input(shape=(self._max_seq_len,), dtype='float32', name='Input-Token')
        segment_ids = Input(shape=(self._max_seq_len,), dtype='float32', name='Input-Segment')
        masked_ids = Input(shape=(self._max_seq_len,), dtype='float32', name='Input-Masked')
        refexp_sentence = [input_ids, segment_ids, masked_ids]

        refexp_pos = Input(shape=(self._max_seq_len,), name='Input-pos')

        # bert layer
        # input: (BATCH_SIZE X [MAX_SEQ_LEN, MAX_SEQ_LEN])
        # output: (BATCH_SIZE X MAX_SEQ_LEN X BERT_SIZE)
        X_refexp_sentence = updated_bert_model(refexp_sentence)

        # dense layer
        # input: (BATCH_SIZE X MAX_SEQ_LEN X 256)
        # output: (BATCH_SIZE X MAX_SEQ_LEN X WORD_EMBEDDING_SIZE)
        #X_refexp_sentence = TimeDistributed(Dense(self._embedding_dim, activation='relu', kernel_initializer='random_normal'))(X_refexp_sentence)

        # embedding layer
        # input: (BATCH_SIZE X MAX_SEQ_LEN)
        # output: (BATCH_SIZE X MAX_SEQ_LEN X WORD_EMBEDDING_SIZE)
        X_refexp_pos = Embedding(input_dim=n_pos + 2, output_dim=768,
                       input_length=self._max_seq_len, mask_zero=True, trainable=True,
                       embeddings_initializer='random_normal')(refexp_pos)

        #bilstm layer
        # input: (BATCH_SIZE X MAX_SEQ_LEN X WORD_EMBEDDING_SIZE)
        # output: (BATCH_SIZE X MAX_SEQ_LEN X WORD_EMBEDDING_SIZE)
        X_refexp_pos = Bidirectional(LSTM(units=384, return_sequences=True, dropout=0.5,
                                kernel_initializer='random_normal'))(X_refexp_pos)

        # merge layer
        # input: (BATCH_SIZE X MAX_SEQ_LEN X WORD_EMBEDDING_SIZE)
        # output: (BATCH_SIZE X MAX_SEQ_LEN X WORD_EMBEDDING_SIZE)
        X_refexp = Average()([X_refexp_sentence, X_refexp_pos])

        #masking_layer = Masking()
        #X_refexp = masking_layer(X_refexp)

        # dense layer
        # input: (BATCH_SIZE X MAX_SEQ_LEN X WORD_EMBEDDING_SIZE)
        # output: (BATCH_SIZE X MAX_SEQ_LEN X WORD_EMBEDDING_SIZE)
        #X_refexp = TimeDistributed(Dense(int(self._embedding_dim / 2), activation='relu', kernel_initializer='random_normal'))(X_refexp)

        #X_refexp = Masking(mask_value=0)(X_refexp)

        # crf layer
        # input: (BATCH_SIZE X MAX_SEQ_LEN X 2*WORD_EMBEDDING_SIZE)
        # output: (BATCH_SIZE X MAX_SEQ_LEN X NO_OF_TAGS)
        X_refexp = CRF(n_tags + 1, sparse_target=True)(X_refexp)

        # input [(BATCH_SIZE X MAX_SEQ_LEN), (BATCH_SIZE, MAX_SEQ_LEN)], (MAX_SEQ_LEN,)
        # output (BATCH_SIZE X MAX_SEQ_LEN X NO_OF_TAGS)
        model = Model(inputs=[refexp_sentence[0], refexp_sentence[1], refexp_sentence[2], refexp_pos], outputs=X_refexp)

        return updated_bert_model, model

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

        bert_model = self._create_bert_keras_model()
        X = bert_model.get_layer(index=-9).output
        shared_bert_model = Model(inputs=bert_model.input, outputs=X)

        # input layer
        # ner_sentence: [(NER task ids (MAX_SEQ_LEN, ), NER task segment ids (MAX_SEQ_LEN, )]
        # ner_pos: NER task pos
        ner_ids = Input(shape=(self._max_seq_len,), dtype='float32', name='Input-Token')
        ner_segment_ids = Input(shape=(self._max_seq_len,), dtype='float32', name='Input-Segment')
        ner_masked = Input(shape=(self._max_seq_len,), dtype='float32', name='Input-Masked')
        ner_sentence = [ner_ids, ner_segment_ids, ner_masked]

        ner_pos = Input(shape=(self._max_seq_len, ))

        # input layer
        # refexp_sentence: [(RE task ids (MAX_SEQ_LEN, ), RE task segment ids (MAX_SEQ_LEN, )]
        # refexp_pos: RE task pos
        refexp_ids = Input(shape=(self._max_seq_len,), dtype='float32', name='Input-Token')
        refexp_segment_ids = Input(shape=(self._max_seq_len,), dtype='float32', name='Input-Segment')
        refexp_masked = Input(shape=(self._max_seq_len,), dtype='float32', name='Input-Mased')
        refexp_sentence = [refexp_ids, refexp_segment_ids, refexp_masked]

        refexp_pos = Input(shape=(self._max_seq_len,))

        masking_layer = Masking(mask_value=0)
        X_ner_sentence = [masking_layer(n) for n in ner_sentence]
        X_refexp_sentence = [masking_layer(n) for n in refexp_sentence]

        # bert layer
        # input: (BATCH_SIZE X MAX_SEQ_LEN)
        # output: (BATCH_SIZE X MAX_SEQ_LEN X BERT_SIZE)
        X_ner_sentence = shared_bert_model(X_ner_sentence)
        X_refexp_sentence = shared_bert_model(X_refexp_sentence)

        # dense layer
        # input: (BATCH_SIZE X MAX_SEQ_LEN X BERT_SIZE)
        # output: (BATCH_SIZE X MAX_SEQ_LEN X 256)
        #shared_dense_layer_1 = TimeDistributed(Dense(256, activation='relu', kernel_initializer='random_normal'))
        #X_ner_sentence = shared_dense_layer_1(X_ner_sentence)
        #X_refexp_sentence = shared_dense_layer_1(X_refexp_sentence)

        # dense layer
        # input: (BATCH_SIZE X MAX_SEQ_LEN X 256)
        # output: (BATCH_SIZE X MAX_SEQ_LEN X WORD_EMBEDDING_SIZE)
        #shared_dense_layer_2 = TimeDistributed(Dense(self._embedding_dim, activation='relu', kernel_initializer='random_normal'))
        #X_ner_sentence = shared_dense_layer_2(X_ner_sentence)
        #X_refexp_sentence = shared_dense_layer_2(X_refexp_sentence)

        # embedding layer
        # input: (BATCH_SIZE X MAX_SEQ_LEN)
        # output: (BATCH_SIZE X MAX_SEQ_LEN X WORD_EMBEDDING_SIZE)
        shared_pos_embedding_layer = Embedding(input_dim=n_source_pos + 2, output_dim=768,
                                               input_length=self._max_seq_len, mask_zero=True, trainable=True,
                                               embeddings_initializer='random_normal')
        X_ner_pos = shared_pos_embedding_layer(ner_pos)
        X_refexp_pos = shared_pos_embedding_layer(refexp_pos)

        #bilstm layer
        # input: (BATCH_SIZE X MAX_SEQ_LEN X WORD_EMBEDDING_SIZE)
        # output: (BATCH_SIZE X MAX_SEQ_LEN X WORD_EMBEDDING_SIZE)
        shared_pos_bilstm_layer = Bidirectional(LSTM(units=384, return_sequences=True, dropout=0.5,
                                                     kernel_initializer='random_normal'))
        X_ner_pos = shared_pos_bilstm_layer(X_ner_pos)
        X_refexp_pos = shared_pos_bilstm_layer(X_refexp_pos)

        #merge layer
        # input: (BATCH_SIZE X MAX_SEQ_LEN X WORD_EMBEDDING_SIZE)
        # output: (BATCH_SIZE X MAX_SEQ_LEN X WORD_EMBEDDING_SIZE)
        X_ner = Average()([X_ner_sentence, X_ner_pos])
        X_refexp = Average()([X_refexp_sentence, X_refexp_pos])

        #masking_layer = Masking()
        #X_ner = masking_layer(X_ner)
        #X_refexp = masking_layer(X_refexp)

        # dense layer
        # input: (BATCH_SIZE X MAX_SEQ_LEN X WORD_EMBEDDING_SIZE)
        # output: (BATCH_SIZE X MAX_SEQ_LEN X WORD_EMBEDDING_SIZE)
        #X_ner = TimeDistributed(Dense(int(self._embedding_dim/2), activation='relu', kernel_initializer='random_normal'))(X_ner)
        #X_refexp = TimeDistributed(Dense(int(self._embedding_dim/2), activation='relu', kernel_initializer='random_normal'))(X_refexp)

        #X_ner, X_refexp = Masking(mask_value=0)(X_ner), Masking(mask_value=0)(X_refexp)
        # crf layer
        # input: (BATCH_SIZE X MAX_SEQ_LEN X WORD_EMBEDDING_SIZE)
        # output: (BATCH_SIZE X MAX_SEQ_LEN X NO_OF_TAGS)
        X_ner = CRF(n_source_tags + 1, sparse_target=True)(X_ner)
        X_refexp = CRF(n_target_tags + 1, sparse_target=True)(X_refexp)

        ner_model = Model(inputs=ner_sentence+[ner_pos], output=X_ner)
        refexp_model = Model(inputs=refexp_sentence+[refexp_pos], output=X_refexp)

        return ner_model, refexp_model
