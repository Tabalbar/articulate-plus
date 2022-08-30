import os
import re
from collections import Counter
from itertools import islice

import bert
import numpy as np
import tensorflow as tf
from bert.tokenization.bert_tokenization import FullTokenizer
from sklearn.model_selection import train_test_split

from .embedding import Embedding

# Copyright 2019 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Functions and classes related to optimization (weight updates)."""


class WarmUp(tf.keras.optimizers.schedules.LearningRateSchedule):
    """Applys a warmup schedule on a given learning rate decay schedule."""

    def __init__(
            self,
            initial_learning_rate,
            decay_schedule_fn,
            warmup_steps,
            power=1.0,
            name=None):
        super(WarmUp, self).__init__()
        self.initial_learning_rate = initial_learning_rate
        self.warmup_steps = warmup_steps
        self.power = power
        self.decay_schedule_fn = decay_schedule_fn
        self.name = name

    def __call__(self, step):
        with tf.name_scope(self.name or 'WarmUp') as name:
            # Implements polynomial warmup. i.e., if global_step < warmup_steps, the
            # learning rate will be `global_step/num_warmup_steps * init_lr`.
            global_step_float = tf.cast(step, tf.float32)
            warmup_steps_float = tf.cast(self.warmup_steps, tf.float32)
            warmup_percent_done = global_step_float / warmup_steps_float
            warmup_learning_rate = (
                    self.initial_learning_rate *
                    tf.math.pow(warmup_percent_done, self.power))
            return tf.cond(global_step_float < warmup_steps_float,
                           lambda: warmup_learning_rate,
                           lambda: self.decay_schedule_fn(step),
                           name=name)

    def get_config(self):
        return {
            'initial_learning_rate': self.initial_learning_rate,
            'decay_schedule_fn': self.decay_schedule_fn,
            'warmup_steps': self.warmup_steps,
            'power': self.power,
            'name': self.name
        }


def create_optimizer(init_lr, num_train_steps, num_warmup_steps):
    """Creates an optimizer with learning rate schedule."""
    # Implements linear decay of the learning rate.
    learning_rate_fn = tf.keras.optimizers.schedules.PolynomialDecay(
        initial_learning_rate=init_lr,
        decay_steps=num_train_steps,
        end_learning_rate=0.0)
    if num_warmup_steps:
        learning_rate_fn = WarmUp(initial_learning_rate=init_lr,
                                  decay_schedule_fn=learning_rate_fn,
                                  warmup_steps=num_warmup_steps)
    optimizer = AdamWeightDecay(
        learning_rate=learning_rate_fn,
        weight_decay_rate=0.01,
        beta_1=0.9,
        beta_2=0.999,
        epsilon=1e-6,
        exclude_from_weight_decay=['layer_norm', 'bias'])
    return optimizer


class AdamWeightDecay(tf.keras.optimizers.Adam):
    """Adam enables L2 weight decay and clip_by_global_norm on gradients.

    Just adding the square of the weights to the loss function is *not* the
    correct way of using L2 regularization/weight decay with Adam, since that will
    interact with the m and v parameters in strange ways.

    Instead we want ot decay the weights in a manner that doesn't interact with
    the m/v parameters. This is equivalent to adding the square of the weights to
    the loss with plain (non-momentum) SGD.
    """

    def __init__(self,
                 learning_rate=0.001,
                 beta_1=0.9,
                 beta_2=0.999,
                 epsilon=1e-7,
                 amsgrad=False,
                 weight_decay_rate=0.0,
                 include_in_weight_decay=None,
                 exclude_from_weight_decay=None,
                 name='AdamWeightDecay',
                 **kwargs):
        super(AdamWeightDecay, self).__init__(
            learning_rate, beta_1, beta_2, epsilon, amsgrad, name, **kwargs)
        self.weight_decay_rate = weight_decay_rate
        self._include_in_weight_decay = include_in_weight_decay
        self._exclude_from_weight_decay = exclude_from_weight_decay

    @classmethod
    def from_config(cls, config):
        """Creates an optimizer from its config with WarmUp custom object."""
        custom_objects = {'WarmUp': WarmUp}
        return super(AdamWeightDecay, cls).from_config(
            config, custom_objects=custom_objects)

    def _prepare_local(self, var_device, var_dtype, apply_state):
        super(AdamWeightDecay, self)._prepare_local(var_device, var_dtype,
                                                    apply_state)
        apply_state['weight_decay_rate'] = tf.constant(
            self.weight_decay_rate, name='adam_weight_decay_rate')

    def _decay_weights_op(self, var, learning_rate, apply_state):
        do_decay = self._do_use_weight_decay(var.name)
        if do_decay:
            return var.assign_sub(
                learning_rate * var *
                apply_state['weight_decay_rate'],
                use_locking=self._use_locking)
        return tf.no_op()

    def apply_gradients(self, grads_and_vars, name=None):
        grads, tvars = list(zip(*grads_and_vars))
        (grads, _) = tf.clip_by_global_norm(grads, clip_norm=1.0)
        return super(AdamWeightDecay, self).apply_gradients(zip(grads, tvars))

    def _get_lr(self, var_device, var_dtype, apply_state):
        """Retrieves the learning rate with the given state."""
        if apply_state is None:
            return self._decayed_lr_t[var_dtype], {}

        apply_state = apply_state or {}
        coefficients = apply_state.get((var_device, var_dtype))
        if coefficients is None:
            coefficients = self._fallback_apply_state(var_device, var_dtype)
            apply_state[(var_device, var_dtype)] = coefficients

        return coefficients['lr_t'], dict(apply_state=apply_state)

    def _resource_apply_dense(self, grad, var, apply_state=None):
        lr_t, kwargs = self._get_lr(var.device, var.dtype.base_dtype, apply_state)
        decay = self._decay_weights_op(var, lr_t, apply_state)
        with tf.control_dependencies([decay]):
            return super(AdamWeightDecay, self)._resource_apply_dense(
                grad, var, **kwargs)

    def _resource_apply_sparse(self, grad, var, indices, apply_state=None):
        lr_t, kwargs = self._get_lr(var.device, var.dtype.base_dtype, apply_state)
        decay = self._decay_weights_op(var, lr_t, apply_state)
        with tf.control_dependencies([decay]):
            return super(AdamWeightDecay, self)._resource_apply_sparse(
                grad, var, indices, **kwargs)

    def get_config(self):
        config = super(AdamWeightDecay, self).get_config()
        config.update({
            'weight_decay_rate': self.weight_decay_rate,
        })
        return config

    def _do_use_weight_decay(self, param_name):
        """Whether to use L2 weight decay for `param_name`."""
        if self.weight_decay_rate == 0:
            return False

        if self._include_in_weight_decay:
            for r in self._include_in_weight_decay:
                if re.search(r, param_name) is not None:
                    return True

        if self._exclude_from_weight_decay:
            for r in self._exclude_from_weight_decay:
                if re.search(r, param_name) is not None:
                    return False
        return True


# ==============================================================================

class BertEmbedding(Embedding):
    def __init__(self, config):
        super().__init__(config=config)

        if config['train']:
            self._batch_size = config['train']['batch_size']
            self._epochs = config['train']['epochs']
            self._shuffle = config['train']['shuffle']

        self._MAX_SEQ_LEN = config['max_seq_len']
        self._HALF_MAX_SEQ_LEN = self._MAX_SEQ_LEN / 2

        BERT_MODEL_DIR = '../'
        BERT_MODEL_NAME = 'uncased_L-6_H-128_A-2/'

        self._BERT_CHECKPOINT_DIR = os.path.join(BERT_MODEL_DIR, BERT_MODEL_NAME)
        self._BERT_CHECKPOINT_FILE = os.path.join(self._BERT_CHECKPOINT_DIR, "bert_model.ckpt")
        self._BERT_CONFIG_FILE = os.path.join(self._BERT_CHECKPOINT_DIR, "bert_config.json")
        self._BERT_VOCAB_FILE = os.path.join(self._BERT_CHECKPOINT_DIR, "vocab.txt")

        self._tokenizer = FullTokenizer(vocab_file=os.path.join(self._BERT_CHECKPOINT_DIR, "vocab.txt"),
                                        do_lower_case=False)

        self._idx2labels = None
        self._labels2idx = None
        self._n_labels = -1

    def _chunk(self, it, size):
        it = iter(it)
        return iter(lambda: tuple(islice(it, size)), ())

    def _tokenize(self, sentence):
        tokens = self._tokenizer.tokenize(sentence)
        '''
        Truncating:
        ['[CLS],the','man','runs','away','from','here','quickly','[SEP]'] with MAX_SEQ_LEN=5 becomes:
        ['[CLS]','the','man','runs','[SEP]',]
        '''
        tokens = tokens[:self._MAX_SEQ_LEN - 2]  # We leave 2 spots open, one [CLS] and one [SEP] token.
        tokens = ['[CLS]'] + tokens + ['[SEP]']  # Now add the two special tokens.

        '''
        Padding:
        Suppose MAX_SEQ_LEN=5 and input is ['[CLS]','the','man','runs','[SEP]'].
        Then, tokens+['PAD']*(MAX_SEQ_LEN-len(input)) will do nothing.

        But, for MAX_SEQ_LEN=8,
        tokens+['PAD']*(MAX_SEQ_LEN-len(input)) becomes:
        [['CLS'],'the','man','runs','[SEP]','[PAD]','[PAD]','[PAD]']

        '''
        no_of_pads = self._MAX_SEQ_LEN - len(tokens)
        input_mask = [1] * len(tokens) + [0] * no_of_pads
        tokens += ['[PAD]'] * no_of_pads
        input_id = self._tokenizer.convert_tokens_to_ids(tokens)
        segment_id = [0] * len(tokens)  # useful when dealing with two sentences, otherwise all zeros.

        return input_id, input_mask, segment_id

    def _tokenize_all(self, sentences):
        for sentence in sentences:
            input_id, input_mask, segment_id = self._tokenize(sentence)
            yield input_id, input_mask, segment_id

    def _tokenize_by_range(self, sentence, token):
        '''
        Ex situation:
        sentence="this safe neighborhood is a safesh place to live"
        tokens=["this safe neighborhood","is","a safesh place","to","live"]

        We want to get the embedding of "a safe place".
        What we know is that bert_tokenized = ['this','safe','neighborhood','is','a','safe',''##sh','place','to','live'].
        So we want to add up embedding of bert_tokenized[4:8].
        '''
        word, token_start_char = token
        # text = "this safe neighborhood is a safesh place to live" but remember bert has 512 word limit
        # token_start_char=token.idx = 26 (since "a safesh place" starts at index 26).
        # token_start_char=token.idx
        # start_index = len(['this','safe','neighborhood','is']) = 4
        start_index = len(self._tokenizer.tokenize(sentence[:token_start_char]))
        # end_index = 4 + len(['a','safe',''##sh','place']) = 8
        end_index = start_index + len(self._tokenizer.tokenize(word))

        tokens = self._tokenizer.tokenize(sentence)
        left_range, right_range = self._get_valid_span(start_index, len(tokens))
        tokens = tokens[left_range:right_range]
        if left_range > 0:
            start_index -= left_range
            end_index -= left_range
        sentence = ' '.join(tokens)
        sentence = sentence.replace(' ##', '')

        input_id, mask_id, segment_id = self._tokenize(sentence)

        return input_id, mask_id, segment_id, start_index, end_index

    def _tokenize_all_by_range(self, sentences, tokens):
        for sentence, token in zip(sentences, tokens):
            input_id, input_mask, segment_id, start_index, end_index = self._tokenize_by_range(sentence, token)
            yield (input_id, input_mask, segment_id, start_index, end_index)

    def partially_contains(self, sentence, token):
        return True

    def contains(self, sentence, token):
        return True  # Bert uses subwords hence all words are represented by Bert embeddings

    def _get_valid_span(self, token_index, tokens_length):
        if token_index < self._HALF_MAX_SEQ_LEN:
            return 0, min(self._MAX_SEQ_LEN, tokens_length)
        left = max(token_index - self._HALF_MAX_SEQ_LEN, 0)
        right = min(token_index + (self._HALF_MAX_SEQ_LEN), tokens_length)
        l_diff = self._HALF_MAX_SEQ_LEN - (token_index - left)
        r_diff = (self._HALF_MAX_SEQ_LEN) - (right - token_index)
        left = max(0, left - r_diff)
        right = min(tokens_length, right + l_diff)
        return int(left), int(right)

    def get_token_embedding(self, sentence, token):
        input_id, _, _, start_index, end_index = self._tokenize_by_range(sentence, token)
        input_ids = np.asarray([input_id], dtype='int32')
        sentence_embedding = self.embedding_model(input_ids)[0]
        token_embedding = np.average(sentence_embedding[start_index:end_index], axis=0)
        return token_embedding  # shape is (768,)

    def get_all_token_embeddings(self, sentences, tokens):
        if self._verbose:
            print("Verbose: Started retrieving embeddings for", len(tokens), "tokens")

        ranges = self._tokenize_all_by_range(sentences, tokens)
        start_end_indices = []
        token_embeddings = []
        total_results = 0
        for idx, range_chunk in enumerate(self._chunk(ranges, 500)):
            input_id_chunk = [r[0] for r in range_chunk]
            start_end_indices += [(r[3], r[4]) for r in range_chunk]
            sentence_embeddings = self.embedding_model(np.asarray(input_id_chunk, dtype='int32'))

            for idx, (sentence_embedding, indices) in enumerate(zip(sentence_embeddings, start_end_indices)):
                start_index, end_index = indices[0], indices[1]
                token_embedding = sentence_embedding[start_index:end_index]
                token_embeddings.append(sum(token_embedding) / len(token_embedding))
                if self._verbose:
                    total_results += token_embeddings[0].shape[0]
                    if idx % 10000 == 0:
                        print("Verbose: retrieved", int(total_results / self._dims), "token embeddings out of",
                              len(tokens), "total tokens")

        token_embeddings = np.vstack(token_embeddings)
        if self._verbose:
            print("Verbose: Completed retrieving", token_embeddings.shape, "token embeddings")

        return token_embeddings  # shape is (batch_size X 768)

    def get_sentence_embedding(self, sentence, only_important_phrases=True):
        input_id, _, _ = self._tokenize(sentence)
        input_ids = np.asarray([input_id], dtype='int32')
        sentence_embedding = self.embedding_model(input_ids)[0]
        return sentence_embedding  # shape is (30 X 768)

    def get_all_sentence_embeddings(self, sentences, only_important_phrases=True):
        if self._verbose:
            print("Verbose: Started retrieving embeddings for", len(sentences), "sentences")

        # texts=[sentence.text for sentence in sentences]
        ranges = self._tokenize_all(sentences)
        sentence_embeddings = []
        total_results = 0
        for idx, range_chunk in enumerate(self._chunk(ranges, 500)):
            input_id_chunk = [r[0] for r in range_chunk]
            sentence_embeddings.append(self.embedding_model(np.asarray(input_id_chunk, dtype='int32')))
            if self._verbose:
                total_results += sentence_embeddings[-1].shape[0]
                print("Verbose: retrieved", total_results, "sentences embeddings out of", len(sentences),
                      "total sentences")
        sentence_embeddings = np.vstack(sentence_embeddings)
        if self._verbose:
            print("Verbose: Completed retrieving", sentence_embeddings.shape, "sentence embeddings")
        return sentence_embeddings  # shape is (BATCH_SIZE X MAX_SEQ_LEN X 768)

    def _create_keras_bert_layer(self):
        bert_params = bert.params_from_pretrained_ckpt(self._BERT_CHECKPOINT_DIR)
        bert_layer = bert.BertModelLayer.from_params(bert_params, name="bert")
        return bert_layer

    def _load_pretrained_weights_to_bert_layer(self, bert_layer):
        bert.load_stock_weights(bert_layer, self._BERT_CHECKPOINT_FILE)

    def get_model_architecture(self):
        input_ids = tf.keras.layers.Input(shape=(self._MAX_SEQ_LEN,), dtype='int32', name='input_ids')

        bert_layer = self._create_keras_bert_layer()

        X = bert_layer(input_ids)[:, 0, :]  # CLS token selected from dims [batch_size,MAX_SEQ_LEN,768 features]

        X = tf.keras.layers.Dropout(0.5)(X)
        X = tf.keras.layers.Dropout(0.5)(X)
        X = tf.keras.layers.Dense(units=self._dims, activation="tanh")(X)
        X = tf.keras.layers.Dense(self._n_labels, activation="softmax")(X)

        model = tf.keras.Model(inputs=input_ids, outputs=X)
        model.build(input_shape=(None, self._MAX_SEQ_LEN))
        self._load_pretrained_weights_to_bert_layer(bert_layer)

        return model

    def fit(self, X, y=None):
        if not y:
            print("Verbose: Must provide labels y")
            return

        if self._verbose:
            print("Verbose: Started training embeddings for the", self._model_name, "model")

        pad_token = 'PAD'
        self._label2idx = {t: i + 1 for i, t in enumerate(np.unique(y))}
        self._label2idx[pad_token] = 0
        self._idx2label = {i: w for w, i in self._label2idx.items()}
        self._n_labels = len(self._label2idx.keys())

        X_, y_ = \
            np.asarray([input_id for (input_id, input_mask, segment_id) in self._tokenize_all(X)], dtype='int32'), \
            np.asarray([self._label2idx[label] for label in y])

        if self._model_name:
            model = self.get_model_architecture()

            if self._verbose:
                print("Verbose: Intermediate model for training")
                model.summary()

            X_train, X_test, y_train, y_test = train_test_split(X_, y_, test_size=0.2, random_state=42, \
                                                                stratify=y_, shuffle=True)
            print("Verbose: Training label counts", Counter(y_train))
            print("Verbose: Testing label counts", Counter(y_test))
            train_data_size = len(X_train)
            steps_per_epoch = int(train_data_size / self._batch_size)
            num_train_steps = steps_per_epoch * self._epochs
            num_warmup_steps = int(self._epochs * train_data_size * 0.1 / self._batch_size)

            optimizer = create_optimizer(2e-5, num_train_steps, num_warmup_steps)
            model.compile(optimizer=optimizer,
                          loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=False),
                          metrics=[tf.keras.metrics.SparseCategoricalAccuracy(name="acc")]
                          )
            model.fit(X_train, y_train,
                      validation_data=(X_test, y_test),
                      batch_size=self._batch_size,
                      epochs=self._epochs,
                      shuffle=self._shuffle,
                      verbose=self._verbose)
            bert_layer = model.layers[-6]
        else:
            bert_layer = self._create_keras_bert_layer()

        self.embedding_model = tf.keras.Model(bert_layer.input, bert_layer.output)
        if self._verbose:
            print("Verbose: Final model for training")
            self.embedding_model.summary()

        if self._verbose:
            print("Verbose: Completed training embeddings for the", self._model_name, "model")

    def save(self, file_name=None):
        save_to = None
        if file_name:
            save_to = file_name

        elif not self._model_name:
            save_to = self._model_name + '.pkl'

        if save_to:
            if self._verbose:
                print("Verbose: Started saving embeddings to", self._model_name, ".pkl")

            self.embedding_model.save_weights(save_to)

            if self._verbose:
                print("Verbose: Completed saving embeddings to", self._model_name, ".pkl")
        else:
            print("Verbose: Cannot save.")

    def load(self, file_name=None):
        load_from = None
        if file_name:
            load_from = file_name

        elif self._model_name:
            load_from = self._model_name + '.pkl'

        else:
            if self._verbose:
                print("Verbose: Started loading pre-trained embeddings")

        self._n_labels = 1
        full_model = self.get_model_architecture()
        bert_layer = full_model.layers[-6]
        self.embedding_model = tf.keras.Model(bert_layer.input, bert_layer.output)
        if self._verbose:
            print("Verbose: Embedding model")
            self.embedding_model.summary()

        if load_from:
            if self._verbose:
                print("Verbose: Started loading embeddings from", load_from)
            self.embedding_model.load_weights(load_from)
            if self._verbose:
                print("Verbose: Completed loading embeddings from", load_from)
        else:
            if self._verbose:
                print("Verbose: Completed loading pre-trained embeddings")
