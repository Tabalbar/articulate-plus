import copy
import datetime
import random
from os import path
from collections import Counter

import keras
import numpy as np
from keras import regularizers
from keras.layers import Dense, Input, Embedding, LSTM, Bidirectional, TimeDistributed, Concatenate, Reshape
from keras.models import Sequential, Model
from keras.preprocessing.sequence import pad_sequences
from keras.utils import np_utils
from keras.wrappers.scikit_learn import KerasClassifier
from keras_contrib.layers.crf import CRF, crf_loss, crf_viterbi_accuracy
from keras.callbacks import EarlyStopping

from .dialogue_act_model import DialogueActModel
from .level import Level
from .lstm_base_model import LSTMBASEModel
from .sequence_metrics import SequenceMetrics
from .utils import ClassificationLevelConfig, UseEmbeddingConfig

np.set_printoptions(threshold=np.inf)


class BILSTMCRFModel(LSTMBASEModel):
    def __init__(self):
        super().__init__(name='BILSTMCRFModel', is_sequence_model=True)

    def train(self,
              classification_level=ClassificationLevelConfig.TOP_LEVEL,
              k_cross_validation=5,
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

        self.train_init(
            classification_level,
            k_cross_validation,
            augment_with_paraphrases,
            augment_with_slot_replacement,
            augment_with_synonym_replacement,
            total_versions,
            embedding_type,
            use_tokenizer,
            max_sequence_length,
            max_queries,
            iterations,
            evaluate)

        if self._k_cross_validation == -1:
            fn = self._get_train_no_split
        elif self._k_cross_validation == 1:
            fn = self._get_single_train_test_split
        else:
            fn = self._get_cross_validation_train_test_split

        top_level_performance = None
        bottom_level_performance = None
        two_level_performance = None

        y_pred_norm = Level()
        y_test_norm = Level()
        fold = -1
        for level_info in fn():
            fold += 1
            top_trained_model, bottom_trained_model = None, None
            top_test_data, bottom_test_data = None, None

            if level_info.get_top_level():
                (train, test, X_train, y_train, X_test, y_test, y_test_seq_spans, top_level_setup_idx,
                 top_level_conclusion_idx) = level_info.get_top_level()
                top_test_data = test

                #for i, l in enumerate(self.get_model_architecture(
                #        words=None, tags=None, which_level=ClassificationLevelConfig.TOP_LEVEL).layers):
                #    print(f'layer {i}: {l}')
                #    print(f'has input mask: {l.input_mask}')
                #    print(f'has output mask: {l.output_mask}')

                class_weight = self.get_class_weight(y_train)
                print("Class weights", class_weight)

                top_trained_model = self.load_model(which_level=ClassificationLevelConfig.TOP_LEVEL, subjects=test,
                                                       fold=fold)
                if top_trained_model:
                    print("Found existing model for X_train", len(X_train), X_train[0].shape,
                          "y_train", y_train.shape, Counter(y_train.flatten()),
                          "X_test", len(X_test), X_test[0].shape,
                          "y_test", y_test.shape, Counter(y_test.flatten()),
                          "Classes", self._tag2idx.get_bottom_level())
                else:
                    top_trained_model = self.get_model_architecture(
                        words=None, tags=None, which_level=ClassificationLevelConfig.TOP_LEVEL)

                    print("No existing model for X_train", len(X_train), X_train[0].shape,
                          "y_train", y_train.shape, Counter(y_train.flatten()),
                          "X_test", len(X_test), X_test[0].shape,
                          "y_test", y_test.shape, Counter(y_test.flatten()), "Classes",
                          self._tag2idx.get_bottom_level())

                    start_time = datetime.datetime.now()
                    top_trained_model.fit(X_train,
                                          y_train,
                                          validation_data=(X_test, y_test),
                                          batch_size=300,
                                          epochs=self._iterations,
                                          verbose=1,
                                          callbacks=[
                                              SequenceMetrics(self._idx2tag.get_top_level(), num_inputs=20),
                                              EarlyStopping(
                                                  monitor='val_f1', patience=4, restore_best_weights=True,
                                                  mode='max')])
                    end_time = datetime.datetime.now()
                    print("TIME DURATION", end_time - start_time)
                    self.save_model(
                        which_level=ClassificationLevelConfig.TOP_LEVEL, trained_model=top_trained_model, subjects=test,
                        fold=fold)

                if evaluate:
                    y_pred = top_trained_model.predict(X_test)
                    # this transforms y_pred from one-hot encoding to numerical values (e.g., [0,0,1,0] becomes 2)
                    # the shape of y_pred is 20 X C (i.e., 20 X 4400 when TOTAL_VERSIONS=10 since 4400 contexts are
                    # generated)
                    y_pred = np.argmax(y_pred, axis=2)

                    CLASSES = self._classes.get_top_level()

                    # don't include the extra label representing the "padding" label since that would unfairly boost
                    # performance results.
                    y_pred_norm.set_top_level([])
                    for inst in y_pred:
                        y_pred_norm.get_top_level().append([i for i in inst])

                    y_test = y_test.reshape(y_test.shape[0], y_test.shape[1])
                    y_test_norm.set_top_level([])
                    for inst in y_test:
                        y_test_norm.get_top_level().append([i for i in inst])

                    # The prediction may include too many cases of the "padding" label. For these cases
                    # just generate a random label so that the lengths between prediction and test
                    # are same shape, since anyways prediction was wrong (should not have been the "padding" label.
                    requests = np.unique(
                        [item for sublist in y_test_norm.get_top_level() \
                         for item in sublist if item not in \
                         [top_level_setup_idx, top_level_conclusion_idx, self._tag2idx.get_top_level()['PAD']]])

                    y_test_norm.set_top_level(DialogueActModel.update_setup_and_conclusion_to_other(
                        y=y_test_norm.get_top_level(), setup_key=top_level_setup_idx,
                        conclusion_key=top_level_conclusion_idx, replace_key=top_level_setup_idx))
                    y_pred_norm.set_top_level(DialogueActModel.update_setup_and_conclusion_to_other(
                        y=y_pred_norm.get_top_level(), setup_key=top_level_setup_idx,
                        conclusion_key=top_level_conclusion_idx, replace_key=top_level_setup_idx))

                    for idx in range(len(y_test_norm.get_top_level())):
                        y_pred_len = len(y_pred_norm.get_top_level()[idx])
                        y_test_len = len(y_test_norm.get_top_level()[idx])
                        while y_pred_len != y_test_len:
                            if y_pred_len < y_test_len:
                                y_pred_norm.get_top_level()[idx].insert(
                                    0, random.choice(requests))
                                y_pred_len = len(y_pred_norm.get_top_level()[idx])
                            elif y_pred_len > y_test_len:
                                is_found = False
                                for rev_val in reversed(y_pred_norm.get_top_level()[idx]):
                                    if rev_val not in requests:
                                        y_pred_norm.get_top_level()[idx].pop()
                                        y_pred_len = len(y_pred_norm.get_top_level()[idx])
                                        is_found = False
                                        break
                                if not is_found:
                                    y_pred_norm.get_top_level()[idx].pop()
                                    y_pred_len = len(y_pred_norm.get_top_level()[idx])

                    y_pred_norm.set_top_level(DialogueActModel.adjust_request_if_missing_or_too_many_in_context(
                        y=y_pred_norm.get_top_level(), requests=requests, tag2idx=self._tag2idx.get_top_level(),
                        setup_key=top_level_setup_idx,
                        conclusion_key=top_level_conclusion_idx, replace_key=top_level_setup_idx))

                    print("\n\nTop Level Classifier: " + self._name.get_top_level() + ", Fold: " + str(
                        fold + 1) + ", CLASSES: " + str(CLASSES))
                    top_level_performance = \
                        self._compute_performance(
                            name=self._name.get_top_level(),
                            y_test=y_test_norm.get_top_level(),
                            y_pred=y_pred_norm.get_top_level(),
                            idx2tag=self._idx2tag.get_top_level(),
                            performance_dict=top_level_performance)

            if level_info.get_bottom_level():
                (train, test, X_train, y_train, X_test, y_test, y_test_seq_spans, bottom_level_setup_idx,
                 bottom_level_conclusion_idx) = level_info.get_bottom_level()
                bottom_test_data = test

                bottom_trained_model = self.load_model(which_level=ClassificationLevelConfig.BOTTOM_LEVEL,
                                                          subjects=test, fold=fold)
                if bottom_trained_model:
                    print("Found existing model for X_train", len(X_train), X_train[0].shape,
                          "y_train", y_train.shape, Counter(y_train.flatten()),
                          "X_test", len(X_test), X_test[0].shape,
                          "y_test", y_test.shape, Counter(y_test.flatten()), "Classes",
                          self._tag2idx.get_bottom_level())

                else:
                    bottom_trained_model = self.get_model_architecture(words=None, tags=None,
                                                                       which_level=ClassificationLevelConfig.
                                                                       BOTTOM_LEVEL)

                    print("No existing model for X_train", len(X_train), X_train[0].shape,
                          "y_train", y_train.shape, Counter(y_train.flatten()),
                          "X_test", len(X_test), X_test[0].shape,
                          "y_test", y_test.shape, Counter(y_test.flatten()), "Classes",
                          self._tag2idx.get_bottom_level())

                    start_time = datetime.datetime.now()
                    bottom_trained_model.fit(X_train, y_train, batch_size=300,
                                             validation_data=(X_test, y_test),
                                             epochs=self._iterations, verbose=1,
                                             callbacks=[
                                                 SequenceMetrics(self._idx2tag.get_bottom_level(), num_inputs=len(X_train)),
                                                 EarlyStopping(
                                                     monitor='val_f1', patience=4, restore_best_weights=True,
                                                     mode='max')])
                    end_time = datetime.datetime.now()
                    print("TIME DURATION", end_time - start_time)
                    self.save_model( \
                        which_level=ClassificationLevelConfig.BOTTOM_LEVEL, trained_model=bottom_trained_model,
                        subjects=test, fold=fold)

                if evaluate:
                    y_pred = bottom_trained_model.predict(X_test)
                    # this transforms y_pred from one-hot encoding to numerical values (e.g., [0,0,1,0] becomes 2)
                    # the shape of y_pred is 20 X C (i.e., 20 X 4400 when TOTAL_VERSIONS=10 since 4400 contexts are
                    # generated)

                    y_pred = np.argmax(y_pred, axis=2)
                    CLASSES = self._classes.get_bottom_level()
                    # don't include the extra label representing the "padding" label since that would unfairly boost
                    # performance results.
                    y_pred_norm.set_bottom_level([])
                    for inst in y_pred:
                        y_pred_norm.get_bottom_level().append([i for i in inst])

                    y_test = y_test.reshape(y_test.shape[0], y_test.shape[1])
                    y_test_norm.set_bottom_level([])
                    for inst in y_test:
                        y_test_norm.get_bottom_level().append([i for i in inst])

                    requests = np.unique( \
                        [item for sublist in y_test_norm.get_bottom_level() \
                         for item in sublist if item not in \
                         [self._tag2idx.get_bottom_level()['PAD']]])

                    print("\n\nBottom Level Classifier: " + self._name.get_bottom_level() + ", Fold: " + str(
                        fold + 1) + ", CLASSES: " + str(CLASSES))
                    bottom_level_performance = \
                        self._compute_performance(
                            name=self._name.get_bottom_level(),
                            y_test=y_test_norm.get_bottom_level(),
                            y_pred=y_pred_norm.get_bottom_level(),
                            idx2tag=self._idx2tag.get_bottom_level(),
                            performance_dict=bottom_level_performance)

            yield top_test_data, top_trained_model, bottom_test_data, bottom_trained_model

            if evaluate:
                if y_pred_norm.get_top_level() and y_pred_norm.get_bottom_level():
                    merged_idx2tag = copy.deepcopy(self._idx2tag.get_top_level())
                    offset = len(merged_idx2tag) - 1
                    for k, v in self._idx2tag.get_bottom_level().items():
                        if v == 'PAD':
                            continue
                        if v == 'merged':
                            merged_idx2tag[offset + k] = 'vis'
                        else:
                            merged_idx2tag[offset + k] = v
                    merged_tag2idx = {v: k for k, v in merged_idx2tag.items()}

                    y_test_bottom_level = [idx[-1] + offset for idx in y_test_norm.get_bottom_level()]
                    y_pred_bottom_level = [idx[-1] + offset for idx in y_pred_norm.get_bottom_level()]

                    merged_request = self._tag2idx.get_top_level()['merged']
                    vis_request = merged_request + offset + 1

                    y_test_requests = []
                    for idx, lst in enumerate(y_test_norm.get_top_level()):
                        request_idx = lst.index(merged_request)
                        request = y_test_bottom_level[idx]
                        lst_cpy = copy.deepcopy(lst)
                        lst_cpy[request_idx] = request
                        y_test_requests.append(lst_cpy)

                    y_pred_requests = []
                    for idx, lst in enumerate(y_pred_norm.get_top_level()):
                        request_idx = lst.index(merged_request)
                        request = y_pred_bottom_level[idx]
                        lst_cpy = copy.deepcopy(lst)
                        lst_cpy[request_idx] = request
                        y_pred_requests.append(lst_cpy)

                    print(
                        "\n\nTwo Level Classifier: " + self._name.get_top_level() + ", " +
                        self._name.get_bottom_level() + ", Fold: " + \
                        str(fold + 1))

                    two_level_performance = \
                        self._compute_performance(
                            name='two_level_'+self._name.get_top_level().split('_')[-1],
                            y_test=y_test_requests,
                            y_pred=y_pred_requests,
                            idx2tag=merged_idx2tag,
                            filter_class_labels=['PAD', 'UNK', 'merged', 'conclusion'],
                            performance_dict=two_level_performance)

        self._print_performance(fold=fold + 1, performance_dict=top_level_performance, name=self._name.get_top_level())
        self._print_performance(fold=fold + 1, performance_dict=bottom_level_performance,
                                name=self._name.get_bottom_level())
        self._print_performance(fold=fold + 1, performance_dict=two_level_performance,
                                name=self._name.get_top_level() + ", " + self._name.get_bottom_level())

    def predict(self, top_level_trained_model, bottom_level_trained_model, context_utterances):
        start_idx = 0
        if len(context_utterances) > self._max_queries:
            start_idx = -1 * self._max_queries
        norm_utterances = context_utterances[start_idx:]

        # Create the feature vector.
        level_info = Level()
        if self._classification_level == ClassificationLevelConfig.TOP_LEVEL or self._classification_level == \
                ClassificationLevelConfig.TWO_LEVEL:
            # Step 1: Iterate each utterance and obtain the appropriate one-hot representation for the
            # neural network input.
            training_instance = []
            for idx in range(len(norm_utterances)):
                feature_vector = \
                    self._feature_extractor.get_top_level().create_features_vector(utterances=norm_utterances,
                                                                                   index=idx,
                                                                                   include_surrounding=False,
                                                                                   include_unigrams=True,
                                                                                   include_tag=False,
                                                                                   include_pos=False,
                                                                                   include_dep=False,
                                                                                   include_tag_unigrams=False,
                                                                                   include_pos_unigrams=False,
                                                                                   include_dep_unigrams=False,
                                                                                   include_avg_word_embeddings=False,
                                                                                   include_sentiment=False,
                                                                                   include_utt_length=False,
                                                                                   include_number_of_slots=False,
                                                                                   include_number_of_non_modal_verbs=
                                                                                   False,
                                                                                   include_number_of_wh_words=False)
                training_instance.append(
                    pad_sequences(
                        self._tokenizer.get_top_level().texts_to_sequences(
                            [';'.join(feature_vector)]), self._max_sequence_length))

            # Step 2: Now we have a list of 3 elements, each of shape 1 X 40. Only thing remaining is to pad
            # with 17 more elements of np.zeros((1,40)) appended to the front.
            if len(training_instance) < self._max_queries:
                training_instance = [np.zeros((1, self._max_sequence_length))
                                     for i in enumerate(range(
                        self._max_queries - len(norm_utterances)))] \
                                    + training_instance
            # training_instance=training_instance[:self._max_queries]
            pred = top_level_trained_model.predict(training_instance)
            pred = np.argmax(pred[0][-1])

            pred = self._idx2tag.get_top_level()[pred]  # if pred < 3 else 'conclusion'
            level_info.set_top_level([str(pred)])

        if self._classification_level == ClassificationLevelConfig.BOTTOM_LEVEL or self._classification_level == \
                ClassificationLevelConfig.TWO_LEVEL:
            # Step 1: Iterate each utterance and obtain the appropriate one-hot representation for the neural network
            # input.
            training_instance = []
            for idx in range(len(norm_utterances)):
                feature_vector = \
                    self._feature_extractor.get_bottom_level().create_features_vector(utterances=norm_utterances,
                                                                                      index=idx,
                                                                                      include_surrounding=False,
                                                                                      include_unigrams=True,
                                                                                      include_tag=False,
                                                                                      include_pos=False,
                                                                                      include_dep=False,
                                                                                      include_tag_unigrams=False,
                                                                                      include_pos_unigrams=False,
                                                                                      include_dep_unigrams=False,
                                                                                      include_avg_word_embeddings=False,
                                                                                      include_sentiment=False,
                                                                                      include_utt_length=False,
                                                                                      include_number_of_slots=False,
                                                                                      include_number_of_non_modal_verbs=
                                                                                      False,
                                                                                      include_number_of_wh_words=False)
                training_instance.append(
                    pad_sequences(self._tokenizer.get_bottom_level().texts_to_sequences([';'.join(feature_vector)]),
                                  self._max_sequence_length))

            # Step 2: Now we have a list of 3 elements, each of shape 1 X 40. Only thing remaining is to pad
            # with 17 more elements of np.zeros((1,40)) appended to the front.
            if len(training_instance) < self._max_queries:
                training_instance = [np.zeros((1, self._max_sequence_length)) \
                                     for i in enumerate(range(self._max_queries - len(norm_utterances)))] \
                                    + training_instance

            pred = bottom_level_trained_model.predict(training_instance)
            pred = np.argmax(pred[0][-1])
            pred = self._idx2tag.get_bottom_level()[pred]  # if pred < 3 else 'conclusion'
            level_info.set_bottom_level([str(pred)])
        return level_info

    def load_model(self, which_level, subjects=None, fold=0):
        if which_level == ClassificationLevelConfig.TOP_LEVEL:
            if subjects is not None:
                model_path = self._model_base_path + '_'.join(
                    [str(s) for s in subjects]) + '_' + self._name.get_top_level() + '_' + str(fold) + '.pkl'
            else:
                model_path = self._model_base_path + self._name.get_top_level() + '_' + str(fold) + '.pkl'
            if path.isfile(model_path):
                print("Loading", model_path)
                trained_model = keras.models.load_model(model_path,
                                                        custom_objects={"CRF": CRF, 'crf_loss': crf_loss,
                                                                        'crf_viterbi_accuracy': crf_viterbi_accuracy})
                return trained_model

        elif which_level == ClassificationLevelConfig.BOTTOM_LEVEL:
            if subjects is not None:
                model_path = self._model_base_path + '_'.join(
                    [str(s) for s in subjects]) + '_' + self._name.get_bottom_level() + '_' + str(fold) + '.pkl'
            else:
                model_path = self._model_base_path + self._name.get_bottom_level() + '_' + str(fold) + '.pkl'

            if path.isfile(model_path):
                print("Loading", model_path)
                trained_model = keras.models.load_model(model_path,
                                                        custom_objects={"CRF": CRF, 'crf_loss': crf_loss,
                                                                        'crf_viterbi_accuracy': crf_viterbi_accuracy})
                return trained_model

        return None

    def save_model(self, which_level, trained_model, subjects=None, fold=0):
        if which_level == ClassificationLevelConfig.TOP_LEVEL:
            if subjects is not None:
                model_path = self._model_base_path + '_'.join(
                    [str(s) for s in subjects]) + '_' + self._name.get_top_level() + '_' + str(fold) + '.pkl'
            else:
                model_path = self._model_base_path + self._name.get_top_level() + '_' + str(fold) + '.pkl'
            print("Saving", model_path)
            trained_model.save(model_path)

        elif which_level == ClassificationLevelConfig.BOTTOM_LEVEL:
            if subjects is not None:
                model_path = self._model_base_path + '_'.join(
                    [str(s) for s in subjects]) + '_' + self._name.get_bottom_level() + '_' + str(fold) + '.pkl'
            else:
                model_path = self._model_base_path + self._name.get_bottom_level() + '_' + str(fold) + '.pkl'
            print("Saving", model_path)
            trained_model.save(model_path)

    def get_model_architecture(self, words, tags, which_level):
        embedding_weights, vocab_size, CLASSES = None, None, None
        if which_level == ClassificationLevelConfig.TOP_LEVEL:
            embedding_weights = self._embedding_weights.get_top_level()
            vocab_size = self._vocab_size.get_top_level()
            CLASSES = self._classes.get_top_level()
        elif which_level == ClassificationLevelConfig.BOTTOM_LEVEL:
            embedding_weights = self._embedding_weights.get_bottom_level()
            vocab_size = self._vocab_size.get_bottom_level()
            CLASSES = self._classes.get_bottom_level()

        embedding_dim = embedding_weights[0].shape[0]
        if self._use_embedding_model:
            embedding_layer = Embedding(vocab_size + 1,
                                        embedding_dim,
                                        weights=[embedding_weights],
                                        input_length=self._max_sequence_length,
                                        trainable=True)
        else:
            embedding_layer = Embedding(vocab_size + 1,
                                        embedding_dim,
                                        input_length=self._max_sequence_length)

        lstm = LSTM(units=100, return_sequences=True, recurrent_dropout=0.5, input_shape=(self._max_sequence_length, 1))

        queries = []
        lstm_outputs = []
        for i in range(self._max_queries):
            r = Input(name='r' + str(i), shape=(self._max_sequence_length,))
            queries.append(r)
            e = embedding_layer(r)
            o = lstm(e)
            lstm_outputs.append(Reshape((1, self._max_sequence_length * 100))(o))

        if len(lstm_outputs) > 1:
            outputs = Concatenate(axis=1)(lstm_outputs)
        else:
            outputs = lstm_outputs

        # X = Reshape((MAX_QUERIES, 100))(outputs)
        X = Bidirectional(LSTM(512, return_sequences=True, recurrent_dropout=0.5))(outputs)

        # compute importance for each step
        '''attention_dense = Dense(1,activation='tanh')
        attention = attention_dense(X)
        print("Dense_attn layer SHAPE",attention_dense.input_shape,attention_dense.output_shape)
        print("dimensins after dense",attention.shape)

        attention_flatten=Flatten()
        attention = attention_flatten(attention)
        print("Flatten_attn layer SHAPE",attention_flatten.input_shape,attention_flatten.output_shape)
        print("dimensions after flatten",attention.shape)

        attention_activation = Activation('softmax')
        attention= attention_activation(attention)
        print("Activation_attn layer SHAPE",attention_activation.input_shape,attention_activation.output_shape)
        print("dimensions after activation",attention.shape)

        attention_repeat = RepeatVector(2*512)
        attention = attention_repeat(attention)
        print("Repeat_attn layer SHAPE",attention_repeat.input_shape,attention_repeat.output_shape)
        print("dimensions after repeatvector",attention.shape)

        attention_permute = Permute([2, 1])
        attention = attention_permute(attention)
        print("Permute_attn layer SHAPE",attention_permute.input_shape,attention_permute.output_shape)
        print("dimensions after permute",attention.shape)

        X = multiply([X, attention])
        print("dimensions after multiply",X.shape)

        #lambda_layer = Lambda(lambda xin: K.sum(xin, axis=1), output_shape=(2*512,))
        #X = lambda_layer(X)
        #print("Lambda layer SHAPE",lambda_layer.input_shape, lambda_layer.output_shape)
        #print("dimensions after lambda",X.shape)'''

        dist_layer = Dense(256, kernel_regularizer=regularizers.l2(0.001), activation='relu')
        X = dist_layer(X)
        # print("Dist layer SHAPE",dist_layer.input_shape, dist_layer.output_shape)
        # print("dimensions after dist",X.shape)
        X = TimeDistributed(Dense(100, activation='relu'))(X)

        # it is important that it is len(CLASSES)+1, since one additional "padding" class is required.
        # the "padding" class is the label assigned to fill up the remaining labels out of 20 that are
        # not filled by the actual context utterances
        crf_layer = CRF(len(CLASSES) + 1, sparse_target=True)
        X = crf_layer(X)
        # print("CRF layer SHAPE",crf_layer.input_shape, crf_layer.output_shape)
        # print("dimensions after crf",X.shape)

        model = Model(inputs=queries, outputs=X)
        model.compile(loss=crf_layer.loss_function, optimizer='adam', metrics=[crf_layer.accuracy])
        print("MODEL", model.summary())

        return model
