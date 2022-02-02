import itertools
import os
import re
from os import path

import keras
import keras_bert
import numpy as np
import pandas as pd
from keras.layers import Dense, TimeDistributed
from keras.models import Model, Input
from sklearn.model_selection import KFold

from .referring_expression_extraction_model import ReferringExpressionExtractionModel
from .utils import UseEmbeddingConfig, LearningTypeConfig


class BERTModel(ReferringExpressionExtractionModel):
    def __init__(self):
        super().__init__(name='BERTModel')
        BERT_MODEL_DIR = '../bert_models/'
        BERT_MODEL_NAME = 'cased_L-12_H-768_A-12/'

        self._BERT_CHECKPOINT_DIR = os.path.join(BERT_MODEL_DIR, BERT_MODEL_NAME)
        self._BERT_CHECKPOINT_FILE = os.path.join(self._BERT_CHECKPOINT_DIR, "bert_model.ckpt")
        self._BERT_CONFIG_FILE = os.path.join(self._BERT_CHECKPOINT_DIR, "bert_config.json")
        self._BERT_VOCAB_FILE = os.path.join(self._BERT_CHECKPOINT_DIR, "vocab.txt")

        # self._layer_id=12 #we want the final encoder output
        # self._layer_dict = [7, 15, 23, 31, 39, 47, 55, 63, 71, 79, 87, 95, 103]
        # vocab_dict = {}
        # with open(self._BERT_VOCAB_FILE,"r",encoding="utf-8") as fid:
        #	for line in fid.readlines():
        #		vocab_dict[line.strip()] = len(vocab_dict)
        # self._tokenizer = FullTokenizer(vocab_file=os.path.join(self._BERT_CHECKPOINT_DIR, "vocab.txt"),\
        #	do_lower_case=False)
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

        source_datasets, source_words, source_tags = self._process_data(source_task_csv_files, source_tag_type)
        n_source_words, n_source_tags = len(source_words), len(source_tags)
        source_tag2idx = {t: i + 1 for i, t in enumerate(source_tags)}
        source_tag2idx['PAD'] = 0
        source_idx2tag = {i: w for w, i in source_tag2idx.items()}

        if target_task_csv_files:
            target_datasets, target_words, target_tags = self._process_data(target_task_csv_files, target_tag_type)
            n_target_words, n_target_tags = len(target_words), len(target_tags)
            target_tag2idx = {t: i + 1 for i, t in enumerate(target_tags)}
            target_tag2idx['PAD'] = 0
            # Vocabulary Key:tag_index -> Value:Label/Tag
            target_idx2tag = {i: w for w, i in target_tag2idx.items()}

        if self._learning_type == LearningTypeConfig.TRANSFER_TASK_LEARNING:
            # First train source task with no cross validation.

            # First we load the larger dataset and train a model on that (no cross validation needed).
            # for data in all_data:
            all_data = self._get_train_no_split(source_datasets, source_tag_type, source_words, source_tags)
            data = all_data[0]
            condensed_trained_model, trained_model = self.get_model_architecture(source_words, source_tags)

            # dense_layer=trained_model.layers[-1]
            # trained_model.compile(loss=crf.loss_function,optimizer='adam',metrics=[crf.accuracy])
            trained_model.compile(optimizer=keras.optimizers.Adam(1e-5), \
                                  loss=keras.losses.SparseCategoricalCrossentropy(from_logits=False), \
                                  metrics=[keras.metrics.SparseCategoricalAccuracy(name="acc")])

            trained_model.summary()
            train, \
            test, \
            (X_train_sentences, X_train_segment_ids, X_train_mask_ids), \
            y_train, \
            (X_test_sentences, X_test_segment_ids, X_test_mask_ids), \
            y_test = data[0], data[1], data[2], data[3], data[4], data[5]

            print("Training on X", X_train_sentences.shape, "Training on y", np.expand_dims(y_train, -1).shape)
            print("IDX2TAG", source_idx2tag)

            trained_model.fit([X_train_sentences, X_train_segment_ids], \
                              np.expand_dims(y_train, -1), \
                              batch_size=self._batch_size, \
                              epochs=iterations, verbose=1)
            performance = dict()
            fold = 0
            all_data = self._get_training_data_fn(target_datasets, target_tag_type, target_words, target_tags)

            # For this model trained on large data, now we need to get the output of the BERT (3 layers back: InputLayer->InputLayer->InputLayer->Bert Model->TimeDist(Dense)->TimeDist(Dense)).
            trained_model = Model(condensed_trained_model.inputs, trained_model.layers[-3].outputs)

            # Now add a new dense layer after the Bilstm, with random weights normalizd to unit gaussian, followed by new CRF layer with the new label size of 4 for RefExps.
            X = TimeDistributed(Dense(256, activation='relu', kernel_initializer='random_normal'))(trained_model.output)
            X = TimeDistributed(Dense(n_target_tags + 1, activation='relu', kernel_initializer='random_normal'))(X)

            trained_model = Model(trained_model.input, X)
            trained_model.summary()

            old_weights = trained_model.get_weights()
            for data in all_data:
                # reset all weights back to original weights as preparation for next fold of k-cross-validation.
                trained_model.set_weights(old_weights)

                crf = trained_model.layers[-1]
                trained_model.compile(loss=crf.loss_function, optimizer='adam', metrics=[crf.accuracy])

                train, \
                test, \
                (X_train_sentences, X_train_segment_ids, X_train_mask_ids), \
                y_train, \
                (X_test_sentences, X_test_segment_ids, X_test_mask_ids), \
                y_test = data[0], data[1], data[2], data[3], data[4], data[5]

                print("Training on X", X_train_sentences.shape, "Training on y", np.expand_dims(y_train, -1).shape)
                print("IDX2TAG", target_idx2tag)
                trained_model.fit([X_train_sentences, X_train_segment_ids],
                                  np.expand_dims(y_train, -1),
                                  batch_size=self._batch_size, epochs=iterations, verbose=1)

                # if we want to evaluate for current fold the following accoplishes this.
                if evaluate:
                    y_pred = trained_model.predict([X_test_sentences, X_test_segment_ids])

                    y_pred = np.argmax(y_pred, axis=-1)
                    performance = self._compute_performance(
                        learning_type='transfer_learning', y_test=y_test, y_pred=y_pred, trained_model=trained_model,
                        idx2tag=target_idx2tag, performance_dict=performance, skip_cls_token=True)

                fold += 1
                # Now that we trained this model we can yield it for the current fold. No need to delete it as we simply just update its weights at start of loop.
                yield trained_model

        elif self._learning_type == LearningTypeConfig.MULTI_TASK_LEARNING:
            # First train source task with no cross validation.
            all_data = self._get_train_no_split(source_datasets, source_tag_type, source_words, source_tags)

            # First we load the larger dataset and train a model on that (no cross validation needed).
            # for data in all_data:
            # data=next(all_data)
            data = all_data[0]
            trained_model1, trained_model2 = self.get_shared_model_architecture(
                source_words, source_tags, target_words, target_tags)

            '''
            model1 Layers are Embedding->BiLSTM->Dense->CRF
            model2 Layers are Embedding'->BiLSTM'->Dense'->CRF'

            We want model2 to share the first two layers:
            desired model2 layers are Embedding->BiLSTM->Dense'->CRF'

            '''

            # dense_layer=trained_model1.layers[-1]
            # trained_model1.compile(loss=crf.loss_function,optimizer='adam',metrics=[crf.accuracy])
            trained_model1.compile(optimizer=keras.optimizers.Adam(1e-5), \
                                   loss=keras.losses.SparseCategoricalCrossentropy(from_logits=False),
                                   metrics=[keras.metrics.SparseCategoricalAccuracy(name="acc")])
            trained_model1.summary()

            train, \
            test, \
            (X_train_sentences, X_train_segment_ids, X_train_mask_ids), \
            y_train, \
            (X_test_sentences, X_test_segment_ids, X_test_mask_ids), \
            y_test = data[0], data[1], data[2], data[3], data[4], data[5]

            print("Training on X", X_train_sentences.shape, "Training on y", y_train.shape)
            print("IDX2TAG", source_idx2tag)
            trained_model1.fit([X_train_sentences, X_train_segment_ids],
                               np.expand_dims(y_train, -1), batch_size=self._batch_size,
                               epochs=iterations, verbose=1)

            performance = dict()
            fold = 0
            old_weights = trained_model2.get_weights()
            all_data = self._get_training_data_fn(target_datasets, target_tag_type, target_words, target_tags)
            for data in all_data:
                # reset all weights back to original weights as preparation for next fold of k-cross-validation.
                trained_model2.set_weights(old_weights)

                # dense_layer=trained_model2.layers[-1]
                # trained_model2.compile(loss=crf.loss_function,optimizer='adam',metrics=[crf.accuracy])
                trained_model2.compile(optimizer=keras.optimizers.Adam(1e-5), \
                                       loss=keras.losses.SparseCategoricalCrossentropy(from_logits=False),
                                       metrics=[keras.metrics.SparseCategoricalAccuracy(name="acc")])
                trained_model2.summary()

                train, \
                test, \
                (X_train_sentences, X_train_segment_ids, X_train_mask_ids), \
                y_train, \
                (X_test_sentences, X_test_segment_ids, X_test_mask_ids), \
                y_test = data[0], data[1], data[2], data[3], data[4], data[5]

                print("Training on X", X_train_sentences.shape, "Training on y", y_train.shape)
                print("IDX2TAG", target_idx2tag)
                trained_model2.fit([X_train_sentences, X_train_segment_ids],
                                   np.expand_dims(y_train, -1),
                                   validation_data=([X_test_sentences, X_test_segment_ids], np.expand_dims(y_test, -1)),
                                   batch_size=self._batch_size, epochs=iterations, verbose=1)

                # if we want to evaluate for current fold the following accoplishes this.
                if evaluate:
                    y_pred = trained_model2.predict([X_test_sentences, X_test_segment_ids])
                    y_pred = np.argmax(y_pred, axis=-1)
                    performance = self._compute_performance(
                        learning_type='multi_task_learning', y_test=y_test, y_pred=y_pred, trained_model=trained_model2,
                        idx2tag=target_idx2tag, performance_dict=performance, skip_cls_token=True)

                fold += 1
                # Now that we trained this model we can yield it for the current fold. No need to delete it as we simply just update its weights at start of loop.
                yield trained_model2


        else:
            performance = dict()
            fold = 0
            all_data = self._get_training_data_fn(source_datasets, source_tag_type, source_words, source_tags)
            condensed_trained_model, trained_model = self.get_model_architecture(source_words, source_tags)
            old_weights = trained_model.get_weights()
            for data in all_data:
                trained_model.set_weights(old_weights)

                crf = trained_model.layers[-1]
                trained_model.compile(loss=crf.loss_function, optimizer='adam', metrics=[crf.accuracy])
                trained_model.summary()

                train, \
                test, \
                (X_train_sentences, X_train_segment_ids, X_train_mask_ids), \
                y_train, \
                (X_test_sentences, X_test_segment_ids, X_test_mask_ids), \
                y_test = data[0], data[1], data[2], data[3], data[4], data[5]

                if self._k_cross_validation != -1:
                    print("Training on X", X_train_sentences.shape, "Training on y", y_train.shape, "norm",
                          np.expand_dims(y_train, -1).shape)
                    print("IDX2TAG", source_idx2tag)

                    trained_model.fit([X_train_sentences, X_train_segment_ids],
                                      np.expand_dims(y_train, -1),
                                      validation_data=(
                                          [X_test_sentences, X_test_segment_ids],
                                          np.expand_dims(y_test, -1)),
                                      batch_size=self._batch_size, epochs=iterations, verbose=1)
                else:
                    print("Training on X", X_train_sentences.shape, "Training on y", y_train.shape)
                    print("IDX2TAG", source_idx2tag)
                    trained_model.fit([X_train_sentences, X_train_segment_ids],
                                      np.expand_dims(y_train, -1), batch_size=self._batch_size,
                                      epochs=iterations, verbose=1)

                # if we want to evaluate for current fold the following accoplishes this.
                if evaluate:
                    y_pred = trained_model.predict([X_test_sentences, X_test_segment_ids])
                    y_pred = np.argmax(y_pred, axis=-1)
                    performance = self._compute_performance(
                        learning_type='single_task_learning', y_test=y_test, y_pred=y_pred, trained_model=trained_model,
                        idx2tag=source_idx2tag, performance_dict=performance, skip_cls_token=True)

                fold += 1
                # Now that we trained this model we can yield it for the current fold
                yield trained_model

        if evaluate:
            self._print_performance(fold=fold, performance_dict=performance, name=self._name)

    def predict(self, trained_model, utterance):
        pass

    def _get_train_no_split(self, datasets, tag_type, words, tags):
        # no split so just flatten all the data and return.
        X_per_subject, y_per_subject = self._get_data(datasets, tag_type, words, tags)

        X_sentences = [sentences for (sentences, segment_ids, mask_ids) in [subject for subject in X_per_subject]]
        X_sentences = np.asarray(list(itertools.chain(*X_sentences)))

        X_segment_ids = [segment_ids for (sentences, segment_ids, mask_ids) in [subject for subject in X_per_subject]]
        X_segment_ids = np.asarray(list(itertools.chain(*X_segment_ids)))

        X_mask_ids = [mask_ids for (sentences, segment_ids, mask_ids) in [subject for subject in X_per_subject]]
        X_mask_ids = np.asarray(list(itertools.chain(*X_mask_ids)))

        y = np.asarray(list(itertools.chain(*y_per_subject)))

        return [[None, None, (X_sentences, X_segment_ids, X_mask_ids), y, (None, None, None), None]]

    def _get_single_train_test_split(self, datasets, tag_type, words, tags):
        # Must split across subject verticals not within subjects. We need self._k_cross_validation total folds in our cross validation.
        X_per_subject, y_per_subject = self._get_data(datasets, tag_type, words, tags)
        k_fold = KFold(n_splits=self._k_cross_validation, shuffle=True, random_state=7)

        total_subjects = len(datasets)
        X_p, y_p = np.zeros((total_subjects,)), np.zeros((total_subjects,))

        # indices are split for the 16 subjects, into the two lists, train and test.
        for train, test in k_fold.split(X_p, y_p):
            X_train, y_train = X_per_subject[train], y_per_subject[train]
            X_train_sentences = [np.asarray(sentences, dtype='int32') for (sentences, segment_ids, mask_ids) in
                                 [subject for subject in X_train]]
            X_train_sentences = np.asarray(list(itertools.chain(*X_train_sentences)))
            X_train_segment_ids = [np.asarray(segment_ids, dtype='int32') for (sentences, segment_ids, mask_ids) in
                                   [subject for subject in X_train]]
            X_train_segment_ids = np.asarray(list(itertools.chain(*X_train_segment_ids)))
            X_train_mask_ids = [np.asarray(mask_ids, dtype='int32') for (sentences, segment_ids, mask_ids) in
                                [subject for subject in X_train]]
            X_train_mask_ids = np.asarray(list(itertools.chain(*X_train_mask_ids)))
            y_train = np.asarray(list(itertools.chain(*y_train)))

            X_test, y_test = X_per_subject[test], y_per_subject[test]
            X_test_sentences = [np.asarray(sentences, dtype='int32') for (sentences, segment_ids, mask_ids) in
                                [subject for subject in X_test]]
            X_test_sentences = np.asarray(list(itertools.chain(*X_test_sentences)))
            X_test_segment_ids = [np.asarray(segment_ids, dtype='int32') for (sentences, segment_ids, mask_ids) in
                                  [subject for subject in X_test]]
            X_test_segment_ids = np.asarray(list(itertools.chain(*X_test_segment_ids)))
            X_test_mask_ids = [np.asarray(mask_ids, dtype='int32') for (sentences, segment_ids, mask_ids) in
                               [subject for subject in X_test]]
            X_test_mask_ids = np.asarray(list(itertools.chain(*X_test_mask_ids)))

            y_test = np.asarray(list(itertools.chain(*y_test)))

            # For each fold, we yield our training data. Much better to do this then to store the data in array which takes up RAM!
            return \
                train, \
                test, \
                [(np.asarray(X_train_sentences),
                  np.asarray(X_train_segment_ids),
                  np.asarray(X_train_mask_ids)),
                 y_train,
                 (np.asarray(X_test_sentences),
                  np.asarray(X_test_segment_ids),
                  np.asarray(X_test_mask_ids)),
                 y_test]

    def _get_cross_validation_train_test_split(self, datasets, tag_type, words, tags):
        # Must split across subject verticals not within subjects. We need self._k_cross_validation total folds in our cross validation.
        X_per_subject, y_per_subject = self._get_data(datasets, tag_type, words, tags)
        k_fold = KFold(n_splits=self._k_cross_validation, shuffle=True, random_state=7)

        total_subjects = len(datasets)
        X_p, y_p = np.zeros((total_subjects,)), np.zeros((total_subjects,))

        # indices are split for the 16 subjects, into the two lists, train and test.
        for train, test in k_fold.split(X_p, y_p):
            X_train, y_train = X_per_subject[train], y_per_subject[train]
            X_train_sentences = [np.asarray(sentences, dtype='int32') for (sentences, segment_ids, mask_ids) in
                                 [subject for subject in X_train]]
            X_train_sentences = np.asarray(list(itertools.chain(*X_train_sentences)))
            X_train_segment_ids = [np.asarray(segment_ids, dtype='int32') for (sentences, segment_ids, mask_ids) in
                                   [subject for subject in X_train]]
            X_train_segment_ids = np.asarray(list(itertools.chain(*X_train_segment_ids)))
            X_train_mask_ids = [np.asarray(mask_ids, dtype='int32') for (sentences, segment_ids, mask_ids) in
                                [subject for subject in X_train]]
            X_train_mask_ids = np.asarray(list(itertools.chain(*X_train_mask_ids)))
            y_train = np.asarray(list(itertools.chain(*y_train)))

            X_test, y_test = X_per_subject[test], y_per_subject[test]
            X_test_sentences = [np.asarray(sentences, dtype='int32') for (sentences, segment_ids, mask_ids) in
                                [subject for subject in X_test]]
            X_test_sentences = np.asarray(list(itertools.chain(*X_test_sentences)))
            X_test_segment_ids = [np.asarray(segment_ids, dtype='int32') for (sentences, segment_ids, mask_ids) in
                                  [subject for subject in X_test]]
            X_test_segment_ids = np.asarray(list(itertools.chain(*X_test_segment_ids)))
            X_test_mask_ids = [np.asarray(mask_ids, dtype='int32') for (sentences, segment_ids, mask_ids) in
                               [subject for subject in X_test]]
            X_test_mask_ids = np.asarray(list(itertools.chain(*X_test_mask_ids)))

            y_test = np.asarray(list(itertools.chain(*y_test)))

            # For each fold, we yield our training data. Much better to do this then to store the data in array which takes up RAM!
            yield \
                train, \
                test, \
                (np.asarray(X_train_sentences),
                 np.asarray(X_train_segment_ids),
                 np.asarray(X_train_mask_ids)), \
                y_train, \
                (np.asarray(X_test_sentences),
                 np.asarray(X_test_segment_ids),
                 np.asarray(X_test_mask_ids)), \
                y_test

    def _transform_to_format(self, sentences_pos_tags, n_tags, word2idx, tag2idx):
        input_ids_list = []
        input_masks_list = []
        segment_ids_list = []
        label_id_list = []
        pad_token_label_id = tag2idx['PAD']
        for words_pos_tags in sentences_pos_tags:
            tokens = []
            label_ids = []

            for word, pos, tag in words_pos_tags:
                word_tokens = self._tokenizer.tokenize(word)[1:-1]
                if not word_tokens:
                    word_tokens = "'"
                tokens.extend(word_tokens)
                # Use the real label id for the first token of the word, and
                # padding ids for the remaining tokens
                label_ids.extend([tag2idx[tag]] + [pad_token_label_id] * (len(word_tokens) - 1))

            # Make 2 spaces available so that we can add [CLS] and [SEP]
            tokens = [t.strip() for t in tokens]
            tokens = tokens[: (self._max_seq_len - 2)]
            tokens = ['[CLS]'] + tokens + ['[SEP]']

            label_ids = label_ids[: (self._max_seq_len - 2)]
            label_ids = [pad_token_label_id] + label_ids + [pad_token_label_id]

            # Add padding.
            no_of_pads = self._max_seq_len - len(tokens)

            input_masks_list.append([1] * len(tokens) + [0] * no_of_pads)

            tokens += ['[PAD]'] * no_of_pads

            label_ids += [pad_token_label_id] * no_of_pads

            input_ids = self._tokenizer._convert_tokens_to_ids(tokens)
            input_ids_list.append(input_ids)

            segment_ids_list.append([0] * len(tokens))

            label_id_list.append(label_ids)

        return np.asarray(input_ids_list, dtype='int32'), \
               np.asarray(segment_ids_list, dtype='int32'), \
               np.asarray(input_masks_list, dtype='int32'), \
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
        tags = list(set(all_datasets[tag_type].values))

        return datasets, words, tags

    def _get_data(self, datasets, tag_type, words, tags):
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

        tag2idx = {t: i + 1 for i, t in enumerate(tags)}
        tag2idx[pad_token] = 0
        # Vocabulary Key:tag_index -> Value:Label/Tag
        idx2tag = {i: w for w, i in tag2idx.items()}

        n_tags = len(tag2idx.keys())

        X_per_subject, y_per_subject = [], []
        for dataset in datasets:
            # Store the (word,pos,tag) list for each sentences in the sentences list
            agg_func = lambda s: [[w, p, t] for w, p, t in \
                                  zip(s["Word"].values.tolist(), s['POS'].values.tolist(), s[tag_type].values.tolist())]
            sentences_pos_tags = dataset.groupby("Sentence #").apply(agg_func)

            X, segment_ids, input_masks, y = self._transform_to_format(sentences_pos_tags, n_tags, word2idx, tag2idx)
            X_per_subject.append((X, segment_ids, input_masks))
            y_per_subject.append(y)
        return np.asarray(X_per_subject), np.asarray(y_per_subject)

    def load_model(self, subjects=None, fold=-1):
        if subjects is not None:
            model_path = self._model_base_path + '_'.join([str(s) for s in subjects])
            '_' + self._name + '_' + str(fold) + '.pkl'
        else:
            model_path = self._model_base_path + 'RE_' + self._name + '_' + str(fold) + '.pkl'
        if path.isfile(model_path):
            print("Loading", model_path)
            return keras.models.load_model(model_path)
        return None

    def save_model(self, trained_model, subjects=None, fold=-1):
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
            training=False
            # trainable=['Encoder-{}-MultiHeadSelfAttention-Adapter'.format(i+1) for i in range(layerN)]+
            # ['Encoder-{}-FeedForward-Adapter'.format(i+1) for i in range(layerN)]+
            # ['Encoder-{}-MultiHeadSelfAttention-Norm'.format(i+1) for i in range(layerN)]+
            # ['Encoder-{}-FeedForward-Norm'.format(i+1) for i in range(layerN)]
        )
        return bert_model

    def get_model_architecture(self, words, tags):
        n_words, n_tags = len(words), len(tags)
        word2idx = {w: i + 2 for i, w in enumerate(words)}

        bert_model = self._create_bert_keras_model()
        X = bert_model.get_layer(index=-9).output
        updated_bert_model = Model(inputs=bert_model.input, outputs=X)

        input_ids = Input(shape=(self._max_seq_len,), dtype='float32', name='Input-Token')
        segment_ids = Input(shape=(self._max_seq_len,), dtype='float32', name='Input-Segment')
        masked_ids = Input(shape=(self._max_seq_len,), dtype='float32', name='Input-Mased')
        inputs = [input_ids, segment_ids]

        X = updated_bert_model(inputs)

        X = TimeDistributed(Dense(256, activation='relu', kernel_initializer='random_normal'))(X)

        X = TimeDistributed(Dense(n_tags + 1, activation='relu', kernel_initializer='random_normal'))(X)

        model = Model(inputs=inputs, outputs=X)

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

   This method will return [model1, model2]

   Then, the idea in training is:
    model1.fit() on all the "source" data


   old_weights=model1.get_weights() for Embedding and BiLSTM layers (layers 1 and 2)
   For fold in k_cross_folds:
          model2.set_weights(old_weights)

       model2.fit() on all the "target" data

   This sequential approach to multitask learning is a simple way to allow for different batch sizes (i.e., "source" and "target" datasets are different sizes).

    '''

    def get_shared_model_architecture(self, source_words, source_tags, target_words, target_tags):
        n_source_words, n_source_tags = len(source_words), len(source_tags)
        n_target_words, n_target_tags = len(target_words), len(target_tags)

        source_word2idx = {w: i + 2 for i, w in enumerate(source_words)}

        # input a 64 integer representation vector of sentence
        bert_model = self._create_bert_keras_model()
        X = bert_model.get_layer(index=-9).output
        shared_bert_model = Model(inputs=bert_model.input, outputs=X)

        input_ids1 = Input(shape=(self._max_seq_len,), dtype='float32', name='Input-Token')
        segment_ids1 = Input(shape=(self._max_seq_len,), dtype='float32', name='Input-Segment')
        masked_ids1 = Input(shape=(self._max_seq_len,), dtype='float32', name='Input-Mased')
        input1 = [input_ids1, segment_ids1]

        input_ids2 = Input(shape=(self._max_seq_len,), dtype='float32', name='Input-Token')
        segment_ids2 = Input(shape=(self._max_seq_len,), dtype='float32', name='Input-Segment')
        masked_ids2 = Input(shape=(self._max_seq_len,), dtype='float32', name='Input-Mased')
        input2 = [input_ids2, segment_ids2]

        X1 = shared_bert_model(input1)
        X2 = shared_bert_model(input2)

        shared_dense_layer = TimeDistributed(Dense(256, activation='relu', kernel_initializer='random_normal'))
        X1 = shared_dense_layer(X1)
        X2 = shared_dense_layer(X2)

        X1 = TimeDistributed(Dense(n_source_tags + 1, activation='relu', kernel_initializer='random_normal'))(X1)
        X2 = TimeDistributed(Dense(n_target_tags + 1, activation='relu', kernel_initializer='random_normal'))(X2)

        model1 = Model(inputs=input1, output=X1)
        model2 = Model(inputs=input2, output=X2)

        return model1, model2
