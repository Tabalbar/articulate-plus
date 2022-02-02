from keras import regularizers
from keras.layers import Dense, Embedding, LSTM, Masking
from keras.models import Model, Input
from keras.models import Sequential
import keras

from .lstm_base_model import LSTMBASEModel
from .utils import ClassificationLevelConfig


class LDNNModel(LSTMBASEModel):
    def __init__(self):
        super().__init__(name='LDNNModel', is_sequence_model=False)

    def get_model_architecture(self, words, tags, which_level):
        embedding_weights, vocab_size, CLASSES, total_classes = None, None, None, None
        if which_level == ClassificationLevelConfig.TOP_LEVEL:
            embedding_weights = self._embedding_weights.get_top_level()
            vocab_size = self._vocab_size.get_top_level()
            CLASSES = self._classes.get_top_level()
            total_classes = len(self._idx2tag.get_top_level())
        elif which_level == ClassificationLevelConfig.BOTTOM_LEVEL:
            embedding_weights = self._embedding_weights.get_bottom_level()
            vocab_size = self._vocab_size.get_bottom_level()
            CLASSES = self._classes.get_bottom_level()
            total_classes = len(self._idx2tag.get_bottom_level())

        utterance = Input(shape=(self._max_sequence_length,))
        embedding_dim = embedding_weights[0].shape[0]
        if self._use_embedding_model:
            embedding_layer = Embedding(vocab_size + 1,
                                        embedding_dim,
                                        weights=[embedding_weights],
                                        input_length=self._max_sequence_length,
                                        mask_zero=True,
                                        trainable=False)
        else:
            embedding_layer = Embedding(vocab_size + 1,
                                        embedding_dim,
                                        mask_zero=True,
                                        input_length=self._max_sequence_length)

        X = embedding_layer(utterance)
        X = LSTM(100, return_sequences=True)(X)
        X = LSTM(100)(X)
        X = Masking(mask_value=0)(X)
        X = Dense(total_classes, activation='softmax')(X)

        model = Model(inputs=utterance, outputs=X)
        model.compile(loss='categorical_crossentropy',
                      optimizer=keras.optimizers.Adam(lr=1e-4), metrics=['accuracy'])
        print("MODEL", model.summary())

        return model
