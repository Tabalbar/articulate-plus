import numpy as np
from keras.callbacks import Callback
from sklearn_crfsuite.metrics import flat_f1_score, flat_recall_score, flat_precision_score, flat_classification_report
from collections import Counter

class SequenceMetrics(Callback):
    def __init__(self, idx2tag, num_inputs=4):
        self.idx2tag = idx2tag
        self.num_inputs = num_inputs

    def on_epoch_end(self, epoch, logs={}):
        inp = [vd for vd in self.validation_data[:self.num_inputs]]
        val_predict = (np.asarray(self.model.predict(inp))).round()
        val_predict = np.argmax(val_predict, -1)
        if len(val_predict.shape) == 1:
            val_predict = np.expand_dims(val_predict, -1)

        val_targ = self.validation_data[self.num_inputs]
        if len(val_targ.shape) == 2 and val_targ.shape[-1] > 1:
            val_targ = np.argmax(val_targ, -1)

        if len(val_targ.shape) == 1:
            val_targ = np.expand_dims(val_targ, -1)

        target_name_indices, target_names = zip(
            *[(idx, tag) for idx, tag in sorted(self.idx2tag.items(), key=lambda kv: kv[0]) if
              tag != 'PAD' and tag != 'UNK'])

        print("IDX2TAG", self.idx2tag)
        print("TARGET NAME INDICES", target_name_indices, "TARGET NAMES", target_names)
        print("PREDICT FREQ", Counter(val_predict.flatten()), "ACTUAL FREQ", Counter(val_targ.flatten()))

        _val_f1 = flat_f1_score(
            val_targ, val_predict, average='macro', labels=target_name_indices, zero_division=0)
        _val_recall = flat_recall_score(
            val_targ, val_predict, average='macro', labels=target_name_indices, zero_division=0)
        _val_precision = flat_precision_score(
            val_targ, val_predict, average='macro', labels=target_name_indices, zero_division=0)

        logs['val_f1'] = _val_f1
        logs['val_recall'] = _val_recall
        logs['val_precision'] = _val_precision
        print(" — val_f1: % f — val_precision: % f — val_recall % f" % (_val_f1, _val_precision, _val_recall))

        print(
            flat_classification_report(
                val_targ, val_predict, zero_division=0, target_names=target_names, labels=target_name_indices, digits=2
            )
        )

        return