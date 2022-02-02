import copy
import datetime
from collections import Counter
import itertools

import numpy as np
from sklearn.model_selection import KFold
from sklearn_crfsuite import CRF

from .dialogue_act_model import DialogueActModel
from .level import Level
from .utils import ClassificationLevelConfig
from .utils import UseEmbeddingConfig
from ..corpus_feature_extractor.context_based_feature_maps import ContextBasedFeatureMaps
from ..corpus_feature_extractor.request_based_feature_maps import RequestBasedFeatureMaps
from ..corpus_feature_extractor.sequence_of_sequence_feature_vectors import SequenceOfSequenceFeatureVectors


class CRFModel(DialogueActModel):
    def __init__(self):
        super().__init__(name='CRFModel', is_sequence_model=False)

    def train_init(self,
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

        super().train(
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

        self._feature_extractor = Level()
        if self._classification_level == ClassificationLevelConfig.TOP_LEVEL \
                or self._classification_level == ClassificationLevelConfig.TWO_LEVEL:
            self._feature_extractor.set_top_level(ContextBasedFeatureMaps(
                embedding_model_path=self._embedding_model_path,
                embedding_model_name=self._embedding_model_name))
            self._name.set_top_level('top_level_' + self._name.get_top_level())
        if self._classification_level == ClassificationLevelConfig.BOTTOM_LEVEL \
                or self._classification_level == ClassificationLevelConfig.TWO_LEVEL:
            self._feature_extractor.set_bottom_level(
                RequestBasedFeatureMaps(
                    embedding_model_path=self._embedding_model_path,
                    embedding_model_name=self._embedding_model_name))
            self._name.set_bottom_level('bottom_level_' + self._name.get_bottom_level())

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
                (train, test, X_train, y_train, X_test, y_test, top_level_setup_idx,
                 top_level_conclusion_idx) = level_info.get_top_level()
                top_test_data = test

                top_trained_model = self.load_model(which_level=ClassificationLevelConfig.TOP_LEVEL, subjects=test,
                                                    fold=fold)
                if top_trained_model:
                    print("Found existing model for X_train", X_train.shape, "y_train", y_train.shape,
                          Counter(Counter(list(itertools.chain(*y_train)))),
                          "X_test", X_test.shape, "y_test", y_test.shape,
                          Counter(Counter(list(itertools.chain(*y_test)))), "Classes", self._tag2idx.get_top_level())
                else:
                    top_trained_model = self.get_model_architecture(None, None, -1)
                    print("No existing model for X_train", X_train.shape, "y_train", y_train.shape,
                          Counter(Counter(list(itertools.chain(*y_train)))),
                          "X_test", X_test.shape, "y_test", y_test.shape,
                          Counter(Counter(list(itertools.chain(*y_test)))), "Classes", self._tag2idx.get_top_level())

                    start_time = datetime.datetime.now()
                    top_trained_model.fit(X_train, y_train)
                    end_time = datetime.datetime.now()
                    print("TIME DURATION", end_time - start_time)
                    self.save_model(which_level=ClassificationLevelConfig.TOP_LEVEL, trained_model=top_trained_model,
                                    subjects=test, fold=fold)

                if evaluate:

                    y_pred = top_trained_model.predict(X_test)

                    y_pred_norm.set_top_level(DialogueActModel.update_setup_and_conclusion_to_other(
                        y=y_pred, setup_key='setup', conclusion_key='conclusion', replace_key='setup'))

                    y_test_norm.set_top_level(DialogueActModel.update_setup_and_conclusion_to_other(
                        y=y_test, setup_key='setup', conclusion_key='conclusion', replace_key='setup'))

                    requests = np.unique(
                        [item for sublist in y_test_norm.get_top_level()
                         for item in sublist if item not in
                         ['setup', 'conclusion']])

                    y_pred_norm.set_top_level(DialogueActModel.adjust_request_if_missing_or_too_many_in_context(
                        y=y_pred_norm.get_top_level(), tag2idx=self._tag2idx.get_top_level(), requests=requests,
                        setup_key='setup', conclusion_key='conclusion', replace_key='setup'))

                    y_pred_norm_to_idx = []
                    for inst in y_pred_norm.get_top_level():
                        y_pred_norm_to_idx.append([self._tag2idx.get_top_level()[t] for t in inst])
                    y_pred_norm.set_top_level(y_pred_norm_to_idx)

                    y_test_norm_to_idx = []
                    for inst in y_test_norm.get_top_level():
                        y_test_norm_to_idx.append([self._tag2idx.get_top_level()[t] for t in inst])
                    y_test_norm.set_top_level(y_test_norm_to_idx)

                    print("\n\nTop Level Classifier: " + self._name.get_top_level() + ", Fold: " + str(fold + 1))
                    top_level_performance = \
                        self._compute_performance(
                            name=self._name.get_top_level(),
                            y_test=y_test_norm.get_top_level(),
                            y_pred=y_pred_norm.get_top_level(),
                            idx2tag=self._idx2tag.get_top_level(),
                            performance_dict=top_level_performance)

            if level_info.get_bottom_level():
                (train, test, X_train, y_train, X_test, y_test, bottom_level_setup_idx,
                 bottom_level_conclusion_idx) = level_info.get_bottom_level()
                bottom_test_data = test

                bottom_trained_model = self.load_model(which_level=ClassificationLevelConfig.BOTTOM_LEVEL,
                                                       subjects=test, fold=fold)
                if bottom_trained_model:
                    print("Found existing model for X_train", X_train.shape, "y_train", y_train.shape,
                          Counter(Counter(list(itertools.chain(*y_train)))),
                          "X_test", X_test.shape, "y_test", y_test.shape,
                          Counter(Counter(list(itertools.chain(*y_test)))), "Classes", self._tag2idx.get_bottom_level())

                else:
                    bottom_trained_model = self.get_model_architecture(None, None, -1)

                    print("No existing model for X_train", X_train.shape, "y_train", y_train.shape,
                          Counter(Counter(list(itertools.chain(*y_train)))),
                          "X_test", X_test.shape, "y_test", y_test.shape,
                          Counter(Counter(list(itertools.chain(*y_test)))), "Classes", self._tag2idx.get_bottom_level())

                    start_time = datetime.datetime.now()
                    bottom_trained_model.fit(X_train, y_train)
                    end_time = datetime.datetime.now()
                    print("TIME DURATION", end_time - start_time)
                    self.save_model(subjects=test, which_level=ClassificationLevelConfig.BOTTOM_LEVEL,
                                    trained_model=bottom_trained_model, fold=fold)

                if evaluate:
                    y_test_norm.set_bottom_level(y_test)
                    y_pred = bottom_trained_model.predict(X_test)
                    y_pred_norm.set_bottom_level(y_pred)

                    y_pred_norm_to_idx = []
                    for inst in y_pred_norm.get_bottom_level():
                        y_pred_norm_to_idx.append([self._tag2idx.get_bottom_level()[t] for t in inst])
                    y_pred_norm.set_bottom_level(y_pred_norm_to_idx)

                    y_test_norm_to_idx = []
                    for inst in y_test_norm.get_bottom_level():
                        y_test_norm_to_idx.append([self._tag2idx.get_bottom_level()[t] for t in inst])
                    y_test_norm.set_bottom_level(y_test_norm_to_idx)

                    print("\n\nBottom Level Classifier: " + self._name.get_bottom_level() + ", Fold: " + str(fold + 1))
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
                        if v == 'merged':
                            merged_idx2tag[offset + k] = 'vis'
                        else:
                            merged_idx2tag[offset + k] = v
                    merged_tag2idx = {v: k for k, v in merged_idx2tag.items()}

                    merged_request = self._tag2idx.get_top_level()['merged']
                    vis_request = merged_request + offset + 1

                    y_test_bottom_level = [idx[-1] + offset for idx in y_test_norm.get_bottom_level()]
                    y_test_requests = []
                    for idx, lst in enumerate(y_test_norm.get_top_level()):
                        request_idx = lst.index(merged_request)
                        request = y_test_bottom_level[idx]
                        lst_cpy = copy.deepcopy(lst)
                        lst_cpy[request_idx] = request
                        y_test_requests.append(lst_cpy)

                    y_pred_bottom_level = [idx[-1] + offset for idx in y_pred_norm.get_bottom_level()]
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
                            filter_class_labels=['merged', 'conclusion'],
                            performance_dict=two_level_performance,)

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
            training_instance = []
            for idx in range(len(norm_utterances)):
                feature_vector = \
                    self._feature_extractor.get_top_level().create_features_vector(utterances=norm_utterances,
                                                                                   index=idx,
                                                                                   include_surrounding=False,
                                                                                   include_unigrams=True,
                                                                                   include_tag=True,
                                                                                   include_pos=True,
                                                                                   include_dep=False,
                                                                                   include_tag_unigrams=False,
                                                                                   include_pos_unigrams=True,
                                                                                   include_dep_unigrams=False,
                                                                                   include_avg_word_embeddings=True,
                                                                                   include_sentiment=False,
                                                                                   include_utt_length=False,
                                                                                   include_number_of_slots=True,
                                                                                   include_number_of_non_modal_verbs=
                                                                                   False,
                                                                                   include_number_of_wh_words=False)
                training_instance.append(feature_vector)

            pred = top_level_trained_model.predict_single(training_instance)[-1]
            level_info.set_top_level([pred])

        if self._classification_level == ClassificationLevelConfig.BOTTOM_LEVEL or self._classification_level == \
                ClassificationLevelConfig.TWO_LEVEL:
            training_instance = []
            for idx in range(len(norm_utterances)):
                feature_vector = \
                    self._feature_extractor.get_bottom_level().create_features_vector(utterances=norm_utterances,
                                                                                      index=idx,
                                                                                      include_unigrams=True,
                                                                                      include_tag=True,
                                                                                      include_pos=True,
                                                                                      include_dep=False,
                                                                                      include_tag_unigrams=False,
                                                                                      include_pos_unigrams=True,
                                                                                      include_dep_unigrams=False,
                                                                                      include_avg_word_embeddings=True,
                                                                                      include_sentiment=False,
                                                                                      include_utt_length=False,
                                                                                      include_number_of_slots=True,
                                                                                      include_number_of_non_modal_verbs=
                                                                                      False,
                                                                                      include_number_of_wh_words=False)
                training_instance.append(feature_vector)

            pred = bottom_level_trained_model.predict_single(training_instance)[-1]
            level_info.set_bottom_level([pred])

        return level_info

    '''
    This method retreives the training data, splitting it with train and test. If the use_top_level_information=True, then
    training labels will comprise of request (i.e., "merged") VS nonrequest (i.e., 'setup' and 'conclusion'). Otherwise,
    the training labels will be the requests ('merged','preferencebased','factbased','clarification',...).

    If the user desires the entire training data, the user should set k_cross_validation=-1.

    Return dictionary in which key is the subjects for training an testing, and value is the X_train, y_train, X_test, and y_test data.
    '''

    def _get_train_no_split(self):
        level_info = Level()

        data = self._get_data()

        try:
            setup_idx = self._tag2idx.get_top_level()['setup']
        except ValueError:
            setup_idx = -1

        try:
            conclusion_idx = self._tag2idx.get_top_level()['conclusion']
        except ValueError:
            conclusion_idx = -1

        if self._classification_level == ClassificationLevelConfig.TOP_LEVEL or self._classification_level == ClassificationLevelConfig.TWO_LEVEL:
            subject_name_by_index, X_raw, y_raw, CLASSES, X_utterances = data.get_top_level()
            level_info.set_top_level(
                (None, None, np.asarray(X_raw), np.asarray(y_raw), None, None, setup_idx, conclusion_idx))

        if self._classification_level == ClassificationLevelConfig.BOTTOM_LEVEL or self._classification_level == ClassificationLevelConfig.TWO_LEVEL:
            subject_name_by_index, X_raw, y_raw, CLASSES, X_utterances = data.get_bottom_level()
            level_info.set_bottom_level(
                (None, None, np.asarray(X_raw), np.asarray(y_raw), None, None, setup_idx, conclusion_idx))

        return [level_info]

    '''
    This method retreives the training data, splitting it with train and test. If the use_top_level_information=True, then
    training labels will comprise of request (i.e., "merged") VS nonrequest (i.e., 'setup' and 'conclusion'). Otherwise,
    the training labels will be the requests ('merged','preferencebased','factbased','clarification',...).

    If the user desires a single split between train and test, simply set k_cross_validation=2 and then select the first split result.

    Return dictionary in which key is the subjects for training an testing, and value is the X_train, y_train, X_test, and y_test data.
    '''

    def _get_single_train_test_split(self):
        data = self._get_data()

        kfold = KFold(n_splits=2, shuffle=True, random_state=7)
        if data.get_top_level():
            total_subjects = len(data.get_top_level()[
                                     0])  # both top and bottom subject name by index will have 16 subjects (doesn't matter which one to use here).
        else:
            total_subjects = len(data.get_bottom_level()[0])

        X_p = np.zeros((total_subjects,))
        y_p = np.zeros((total_subjects,))

        # if k_cross_validation=2 this will loop twice, but you just need the split of the first iteration as a user of this class.
        kfolddata = []
        for train, test in kfold.split(X_p, y_p):
            level_info = Level()
            if data.get_top_level():
                subject_name_by_index, X_raw, y_raw, CLASSES, X_utterances = data.get_top_level()

                try:
                    setup_idx = self._tag2idx.get_top_level()['setup']
                except ValueError:
                    setup_idx = -1

                try:
                    conclusion_idx = self._tag2idx.get_top_level()['conclusion']
                except ValueError:
                    conclusion_idx = -1

                X = X_raw
                y = y_raw

                X_train = []
                y_train = []
                X_test = []
                y_test = []

                for inst in train:
                    for span in subject_name_by_index[inst + 5]:
                        X_train += list(X[span[0]:span[0] + len(span)])
                        y_train += list(y[span[0]:span[0] + len(span)])

                for inst in test:
                    span = subject_name_by_index[inst + 5][0]
                    X_test += list(X[span[0]:span[0] + len(span)])
                    y_test += list(y[span[0]:span[0] + len(span)])

                level_info.set_top_level((train, test, np.asarray(X_train), np.asarray(y_train), np.asarray(X_test),
                                          np.asarray(y_test), setup_idx, conclusion_idx))

            if data.get_bottom_level():
                subject_name_by_index, X_raw, y_raw, CLASSES, X_utterances = level_info.get_bottom_level()

                try:
                    setup_idx = self._tag2idx.get_bottom_level()['setup']
                except ValueError:
                    setup_idx = -1

                try:
                    conclusion_idx = self._tag2idx.get_bottom_level()['conclusion']
                except ValueError:
                    conclusion_idx = -1

                X = X_raw
                y = y_raw

                X_train = []
                y_train = []
                X_test = []
                y_test = []

                for inst in train:
                    for span in subject_name_by_index[inst + 5]:
                        X_train += list(X[span[0]:span[0] + len(span)])
                        y_train += list(y[span[0]:span[0] + len(span)])

                for inst in test:
                    span = subject_name_by_index[inst + 5][0]
                    X_test += list(X[span[0]:span[0] + len(span)])
                    y_test += list(y[span[0]:span[0] + len(span)])

                level_info.set_bottom_level((train, test, np.asarray(X_train), np.asarray(y_train), np.asarray(X_test),
                                             np.asarray(y_test), setup_idx, conclusion_idx))
            kfolddata.append(level_info)

            # just go through one itereation of the loop
            return kfolddata

    '''
    This method retreives the training data, splitting it with train and test. If the use_top_level_information=True, then
    training labels will comprise of request (i.e., "merged") VS nonrequest (i.e., 'setup' and 'conclusion'). Otherwise,
    the training labels will be the requests ('merged','preferencebased','factbased','clarification',...).

    Return dictionary in which key is the subjects for training an testing, and value is the X_train, y_train, X_test, and y_test data.
    '''

    def _get_cross_validation_train_test_split(self):
        data = self._get_data()

        kfold = KFold(n_splits=self._k_cross_validation, shuffle=True, random_state=7)

        if data.get_top_level():
            total_subjects = len(data.get_top_level()[
                                     0])  # both top and bottom subject name by index will have 16 subjects (doesn't matter which one to us)
        else:
            total_subjects = len(data.get_bottom_level()[0])

        X_p = np.zeros((total_subjects,))
        y_p = np.zeros((total_subjects,))

        # if k_cross_validation=2 this will loop twice, but you just need the split of the first iteration as a user of this class.
        kfolddata = []
        for train, test in kfold.split(X_p, y_p):
            level_info = Level()
            if data.get_top_level():
                subject_name_by_index, X_raw, y_raw, CLASSES, X_utterances = data.get_top_level()

                try:
                    setup_idx = self._tag2idx.get_top_level()['setup']
                except KeyError:
                    setup_idx = -1

                try:
                    conclusion_idx = self._tag2idx.get_top_level()['conclusion']
                except KeyError:
                    conclusion_idx = -1

                X = X_raw
                y = y_raw

                X_train = []
                y_train = []
                X_test = []
                y_test = []

                for inst in train:
                    for span in subject_name_by_index[inst + 5]:
                        X_train += list(X[span[0]:span[0] + len(span)])
                        y_train += list(y[span[0]:span[0] + len(span)])

                for inst in test:
                    span = subject_name_by_index[inst + 5][0]
                    X_test += list(X[span[0]:span[0] + len(span)])
                    y_test += list(y[span[0]:span[0] + len(span)])

                level_info.set_top_level((train, test, np.asarray(X_train), np.asarray(y_train), np.asarray(X_test),
                                          np.asarray(y_test), setup_idx, conclusion_idx))

            if data.get_bottom_level():
                subject_name_by_index, X_raw, y_raw, CLASSES, X_utterances = data.get_bottom_level()

                try:
                    setup_idx = self._tag2idx.get_bottom_level()['setup']
                except KeyError:
                    setup_idx = -1

                try:
                    conclusion_idx = self._tag2idx.get_bottom_level()['conclusion']
                except KeyError:
                    conclusion_idx = -1

                X = X_raw
                y = y_raw

                X_train = []
                y_train = []
                X_test = []
                y_test = []

                for inst in train:
                    for span in subject_name_by_index[inst + 5]:
                        X_train += list(X[span[0]:span[0] + len(span)])
                        y_train += list(y[span[0]:span[0] + len(span)])

                for inst in test:
                    span = subject_name_by_index[inst + 5][0]
                    X_test += list(X[span[0]:span[0] + len(span)])
                    y_test += list(y[span[0]:span[0] + len(span)])

                level_info.set_bottom_level((train, test, np.asarray(X_train), np.asarray(y_train), np.asarray(X_test),
                                             np.asarray(y_test), setup_idx, conclusion_idx))
            kfolddata.append(level_info)

        return kfolddata

    def _get_data(self):
        level_info = Level()

        if self._classification_level == ClassificationLevelConfig.TOP_LEVEL or self._classification_level == ClassificationLevelConfig.TWO_LEVEL:
            print("Extracting top level data...")
            feature_builder = SequenceOfSequenceFeatureVectors(
                feature_extractor=self._feature_extractor.get_top_level())
            subject_name_by_index, X_raw, y_raw, CLASSES, X_utterances, tag2idx, idx2tag = \
                feature_builder.extract(
                    corpus_path=self._corpus_path,
                    tokenize=self._use_tokenizer,
                    include_setup=True,
                    include_request=True,
                    include_conclusion=True,
                    include_surrounding=True,
                    include_unigrams=True,
                    include_tag=True,
                    include_pos=True,
                    include_dep=False,
                    include_tag_unigrams=False,
                    include_pos_unigrams=True,
                    include_dep_unigrams=False,
                    include_avg_word_embeddings=True,
                    include_sentiment=False,
                    include_utt_length=False,
                    include_number_of_slots=True,
                    include_number_of_non_modal_verbs=False,
                    include_number_of_wh_words=False,
                    IGNORE_CLASSES=['appearance', 'big high level question'],
                    MERGE_CLASSES=['createvis', 'modifyvis', 'factbased', 'preference', 'winmgmt', 'clarification'],
                    is_corpus_json=self._use_paraphrasing,
                    total_versions=self._total_versions)

            self._tag2idx.set_top_level(tag2idx)
            self._idx2tag.set_top_level(idx2tag)
            self._classes.set_top_level(CLASSES)
            level_info.set_top_level((subject_name_by_index, X_raw, y_raw, CLASSES, X_utterances))

        if self._classification_level == ClassificationLevelConfig.BOTTOM_LEVEL or self._classification_level == ClassificationLevelConfig.TWO_LEVEL:
            print("Extracting bottom level data...")
            feature_builder = SequenceOfSequenceFeatureVectors(
                feature_extractor=self._feature_extractor.get_bottom_level())
            subject_name_by_index, X_raw, y_raw, CLASSES, X_utterances, tag2idx, idx2tag = \
                feature_builder.extract(
                    corpus_path=self._corpus_path,
                    tokenize=self._use_tokenizer,
                    include_setup=False,
                    include_request=True,
                    include_conclusion=False,
                    include_surrounding=True,
                    include_unigrams=True,
                    include_tag=True,
                    include_pos=True,
                    include_dep=False,
                    include_tag_unigrams=False,
                    include_pos_unigrams=True,
                    include_dep_unigrams=False,
                    include_avg_word_embeddings=True,
                    include_sentiment=False,
                    include_utt_length=False,
                    include_number_of_slots=True,
                    include_number_of_non_modal_verbs=False,
                    include_number_of_wh_words=False,
                    IGNORE_CLASSES=['appearance', 'big high level question'],
                    MERGE_CLASSES=['createvis', 'modifyvis'],
                    is_corpus_json=self._use_paraphrasing,
                    total_versions=self._total_versions)

            self._tag2idx.set_bottom_level(tag2idx)
            self._idx2tag.set_bottom_level(idx2tag)
            self._classes.set_bottom_level(CLASSES)
            level_info.set_bottom_level((subject_name_by_index, X_raw, y_raw, CLASSES, X_utterances))

        return level_info

    def get_model_architecture(self, words, tags, which_level):
        return CRF(algorithm='lbfgs',
                   c1=0.1,
                   c2=0.1,
                   max_iterations=self._iterations,
                   all_possible_transitions=True)
