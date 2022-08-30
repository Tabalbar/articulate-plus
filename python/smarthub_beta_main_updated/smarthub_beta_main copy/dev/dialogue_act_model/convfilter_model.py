from .utils import ClassificationLevelConfig
from keras import regularizers
from keras.layers import Dense, Input, Embedding, Flatten, Dropout, Conv1D, MaxPooling1D
from keras.layers.merge import concatenate
from keras.models import Sequential, Model

from .lstm_base_model import LSTMBASEModel
from .utils import ClassificationLevelConfig


class CONVFILTERModel(LSTMBASEModel):
    def __init__(self):
        super().__init__(name='CONVFILTERModel', is_sequence_model=False)

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

        sequence_input = Input(shape=(self._max_sequence_length,), dtype='int32')
        embedded_sequences = embedding_layer(sequence_input)

        # Yoon Kim model (https://arxiv.org/abs/1408.5882)
        convs = []
        filter_sizes = [3, 4, 5]  # in the loop, first apply 3 as size, then 4 then 5

        for filter_size in filter_sizes:
            l_conv = Conv1D(filters=128, kernel_size=filter_size, activation='relu')(embedded_sequences)

            # kernel is the filter
            l_pool = MaxPooling1D(pool_size=3)(l_conv)
            # model.add(l_pool)
            convs.append(l_pool)

        l_merge = concatenate(convs, axis=1)

        # activated if extra_convoluted is true at the def
        # add a 1D convnet with global maxpooling, instead of Yoon Kim model
        conv = Conv1D(filters=128, kernel_size=3, activation='relu')(embedded_sequences)
        pool = MaxPooling1D(pool_size=3)(conv)

        extra_conv = True
        if extra_conv == True:
            x = Dropout(0.5)(l_merge)
        else:
            # Original Yoon Kim model
            x = Dropout(0.5)(pool)
        x = Flatten()(x)
        x = Dense(128, activation='relu')(x)
        x = Dropout(0.5)(x)
        # Finally, we feed the output into a Sigmoid layer.
        # The reason why sigmoid is used is because we are trying to achieve a binary classification(1,0)
        # for each of the 6 labels, and the sigmoid function will squash the output between the bounds of 0 and 1.
        preds = Dense(total_classes, kernel_regularizer=regularizers.l2(0.001), activation='sigmoid')(x)
        model = Model(sequence_input, preds)
        model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
        print("Model", model.summary())

        return model
