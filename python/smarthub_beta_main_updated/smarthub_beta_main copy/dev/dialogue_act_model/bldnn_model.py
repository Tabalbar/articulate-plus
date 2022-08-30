from keras import regularizers
from keras.layers import Dense, Embedding, LSTM, Bidirectional, Dropout, Masking
from keras.models import Sequential

from .lstm_base_model import LSTMBASEModel
from .utils import ClassificationLevelConfig


class BLDNNModel(LSTMBASEModel):
    def __init__(self):
        super().__init__(name='BLDNNModel', is_sequence_model=False)

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

        model = Sequential()
        embedding_dim = embedding_weights[0].shape[0]
        if self._use_embedding_model:
            embedding_layer = Embedding(vocab_size + 1,
                                        embedding_dim,
                                        weights=[embedding_weights],
                                        input_length=self._max_sequence_length,
                                        mask_zero=True,
                                        trainable=True)
        else:
            embedding_layer = Embedding(vocab_size + 1,
                                        embedding_dim,
                                        mask_zero=True,
                                        input_length=self._max_sequence_length)

        model.add(embedding_layer)
        model.add(Dropout(0.5))
        model.add(Bidirectional(LSTM(24, input_shape=(self._max_sequence_length, 1),
                                     return_sequences=False, recurrent_dropout=0.5)))
        model.add(Masking(mask_value=0))
        model.add(Dense(total_classes, kernel_regularizer=regularizers.l2(0.001), activation='softmax'))
        model.compile(loss='categorical_crossentropy',
                      optimizer='adam', metrics=['accuracy'])
        print("MODEL", model.summary())
        return model
