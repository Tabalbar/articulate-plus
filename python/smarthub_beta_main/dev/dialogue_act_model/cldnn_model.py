from keras import regularizers
from keras.layers import Dense, Embedding, LSTM, Dropout, Conv1D, MaxPooling1D, Masking
from keras.models import Sequential
import keras
import keras.backend as K

from .lstm_base_model import LSTMBASEModel
from .utils import ClassificationLevelConfig


class CLDNNModel(LSTMBASEModel):
    def __init__(self):
        super().__init__(name='CLDNNModel', is_sequence_model=False)

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
                                        trainable=True)
        else:
            embedding_layer = Embedding(vocab_size + 1,
                                        embedding_dim,
                                        input_length=self._max_sequence_length)

        model.add(embedding_layer)
        model.add(Dropout(0.5))
        model.add(Conv1D(512, 5, activation='relu'))
        model.add(MaxPooling1D(pool_size=4))
        model.add(LSTM(100, return_sequences=True))
        model.add(LSTM(100))
        model.add(Masking(mask_value=0))
        model.add(Dense(total_classes, kernel_regularizer=regularizers.l2(0.001), activation='softmax'))
        model.compile(loss='categorical_crossentropy',
                      optimizer='adam', metrics=['accuracy'])
        print("MODEL", model.summary())
        return model
