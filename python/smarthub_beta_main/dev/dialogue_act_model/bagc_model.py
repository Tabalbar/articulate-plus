import copy
import datetime
import itertools
from collections import Counter

import numpy as np
import scipy
from imblearn.ensemble import BalancedBaggingClassifier
from scipy.sparse.csr import csr_matrix
from sklearn.model_selection import KFold

from .dialogue_act_model import DialogueActModel
from .level import Level
from .utils import ClassificationLevelConfig, UseEmbeddingConfig
from ..corpus_feature_extractor.bow_feature_vectors import BOWFeatureVectors
from ..corpus_feature_extractor.context_based_feature_vectors import ContextBasedFeatureVectors
from ..corpus_feature_extractor.request_based_feature_vectors import RequestBasedFeatureVectors


class BAGCModel(DialogueActModel):
    def __init__(self):
        super().__init__(name='BAGCModel', is_sequence_model=False)

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
            self._feature_extractor.set_top_level(ContextBasedFeatureVectors(
                embedding_model_path=self._embedding_model_path,
                embedding_model_name=self._embedding_model_name))
            self._name.set_top_level('top_level_' + self._name.get_top_level())
        if self._classification_level == ClassificationLevelConfig.BOTTOM_LEVEL \
                or self._classification_level == ClassificationLevelConfig.TWO_LEVEL:
            self._feature_extractor.set_bottom_level(
                RequestBasedFeatureVectors(
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
                (train, test, X_train, y_train, X_test, y_test, y_test_seq_spans, top_level_setup_idx,
                 top_level_conclusion_idx) = level_info.get_top_level()
                top_test_data = test

                top_trained_model = self.load_model(which_level=ClassificationLevelConfig.TOP_LEVEL, subjects=test,
                                                    fold=fold)
                if top_trained_model:
                    print("Found existing model for X_train", X_train.shape, "y_train", y_train.shape, Counter(y_train),
                          "X_test", X_test.shape, "y_test", y_test.shape, Counter(y_test), "Classes",
                          self._tag2idx.get_top_level())
                else:
                    top_trained_model = self.get_model_architecture(None, None, -1)

                    print("No existing model for X_train", X_train.shape, "y_train", y_train.shape, Counter(y_train),
                          "X_test", X_test.shape, "y_test", y_test.shape, Counter(y_test), "Classes",
                          self._tag2idx.get_top_level())

                    start_time = datetime.datetime.now()
                    top_trained_model.fit(X_train,
                                          y_train)
                    end_time = datetime.datetime.now()
                    print("TIME DURATION", end_time - start_time)
                    self.save_model(which_level=ClassificationLevelConfig.TOP_LEVEL, trained_model=top_trained_model,
                                    subjects=test, fold=fold)

                if evaluate:
                    y_pred = top_trained_model.predict(X_test)

                    y_test_norm.set_top_level(DialogueActModel.transform_to_sequence(y_test_seq_spans, y_test))
                    y_test_norm.set_top_level(DialogueActModel.update_setup_and_conclusion_to_other(
                        y=y_test_norm.get_top_level(),
                        setup_key=top_level_setup_idx, conclusion_key=top_level_conclusion_idx,
                        replace_key=top_level_setup_idx))

                    y_pred_norm.set_top_level(DialogueActModel.transform_to_sequence(y_test_seq_spans, y_pred))

                    y_pred_norm.set_top_level(DialogueActModel.update_setup_and_conclusion_to_other(
                        y=y_pred_norm.get_top_level(),
                        setup_key=top_level_setup_idx, conclusion_key=top_level_conclusion_idx,
                        replace_key=top_level_setup_idx))

                    requests = np.unique(
                        [item for sublist in y_test_norm.get_top_level() \
                         for item in sublist if item not in \
                         [top_level_setup_idx, top_level_conclusion_idx]])

                    y_pred_norm.set_top_level(DialogueActModel.adjust_request_if_missing_or_too_many_in_context(
                        y=y_pred_norm.get_top_level(), requests=requests, tag2idx=self._tag2idx.get_top_level(),
                        setup_key=top_level_setup_idx, conclusion_key=top_level_conclusion_idx,
                        replace_key=top_level_setup_idx))

                    #print("ypredtop", Counter(itertools.chain(*y_pred_norm.get_top_level())))

                    print("Top Level Classifier: " + self._name.get_top_level() + ", Fold: " + str(fold + 1))
                    top_level_performance = \
                        self._compute_performance(
                            name=self._name.get_top_level(),
                            y_test=y_test_norm.get_top_level(),
                            y_pred=y_pred_norm.get_top_level(),
                            idx2tag=self._idx2tag.get_top_level(),
                            performance_dict=top_level_performance)

            if level_info.get_bottom_level():
                (train, test, X_train, y_train, X_test, y_test, y_test_seq_spans, setup_idx,
                 conclusion_idx) = level_info.get_bottom_level()
                bottom_test_data = test

                bottom_trained_model = self.load_model(which_level=ClassificationLevelConfig.BOTTOM_LEVEL,
                                                       subjects=test, fold=fold)
                if bottom_trained_model:
                    print("Found existing model for X_train", X_train.shape, "y_train", y_train.shape, Counter(y_train),
                          "X_test", X_test.shape, "y_test", y_test.shape, Counter(y_test), "Classes",
                          self._tag2idx.get_bottom_level())
                else:
                    bottom_trained_model = self.get_model_architecture(None, None, -1)

                    print("No existing model for X_train", X_train.shape, "y_train", y_train.shape, Counter(y_train),
                          "X_test", X_test.shape, "y_test", y_test.shape, Counter(y_test), "Classes",
                          self._tag2idx.get_bottom_level())

                    start_time = datetime.datetime.now()
                    bottom_trained_model.fit(X_train,
                                             y_train)
                    end_time = datetime.datetime.now()
                    print("TIME DURATION", end_time - start_time)
                    self.save_model(which_level=ClassificationLevelConfig.BOTTOM_LEVEL,
                                    trained_model=bottom_trained_model, subjects=test, fold=fold)

                if evaluate:
                    y_pred = bottom_trained_model.predict(X_test)

                    y_test_norm.set_bottom_level(DialogueActModel.transform_to_sequence(y_test_seq_spans, y_test))

                    y_pred_norm.set_bottom_level(DialogueActModel.transform_to_sequence(y_test_seq_spans, y_pred))

                    #print("ypredbottom", Counter(itertools.chain(*y_pred_norm.get_bottom_level())))

                    print("Bottom Level Classifier: " + self._name.get_bottom_level() + ", Fold: " + str(fold + 1))
                    bottom_level_performance = \
                        self._compute_performance(
                            name=self._name.get_bottom_level(),
                            y_test=y_test_norm.get_bottom_level(),
                            y_pred=y_pred_norm.get_bottom_level(),
                            idx2tag=self._idx2tag.get_bottom_level(),
                            performance_dict=bottom_level_performance)

            yield (top_test_data, top_trained_model, bottom_test_data, bottom_trained_model)

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
                            filter_class_labels=['merged', 'conclusion'],
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
            include_avg_word_embeddings = False
            include_sentiment = False
            include_utt_length = False
            include_number_of_slots = False
            include_number_of_non_modal_verbs = False
            include_number_of_wh_words = False

            # Create the feature vector.
            text_feature_vector = self._feature_extractor.get_top_level().create_features_vector(
                utterances=norm_utterances, index=len(norm_utterances) - 1,
                include_surrounding=False,
                include_unigrams=True,
                include_tag=True,
                include_pos=True,
                include_dep=False,
                include_tag_unigrams=False,
                include_pos_unigrams=True,
                include_dep_unigrams=False,
                include_avg_word_embeddings=include_avg_word_embeddings,
                include_sentiment=include_sentiment,
                include_utt_length=include_utt_length,
                include_number_of_slots=include_number_of_slots,
                include_number_of_non_modal_verbs=include_number_of_non_modal_verbs,
                include_number_of_wh_words=include_number_of_wh_words)

            X_tfidf = self._tokenizer.get_top_level().transform([';'.join(text_feature_vector)])

            X_we = None
            X_utt_length = None
            X_sentiment = None
            X_number_of_slots = None
            X_number_of_non_modal_verbs = None
            X_number_of_wh_words = None

            utterance = norm_utterances[len(norm_utterances) - 1]

            if include_avg_word_embeddings:
                we = self._feature_extractor.get_top_level().get_average_word_embeddings(utterances=[utterance])
                if len(we.shape) != 0:
                    if X_we is None:
                        X_we = []
                    X_we.append(we)

            if include_utt_length:
                avg_utt_length = self._feature_extractor.get_top_level().get_average_utt_length(utterances=[utterance])
                if X_utt_length is None:
                    X_utt_length = []
                X_utt_length.append(avg_utt_length)

            if include_sentiment:
                avg_sentiment = self._feature_extractor.get_top_level().get_average_sentiment(utterances=[utterance])
                if X_sentiment is None:
                    X_sentiment = []
                X_sentiment.append(avg_sentiment)

            if include_number_of_slots:
                avg_number_of_slots = self._feature_extractor.get_top_level().get_average_number_of_slots(
                    utterances=[utterance])
                if X_number_of_slots is None:
                    X_number_of_slots = []
                X_number_of_slots.append(avg_number_of_slots)

            if include_number_of_non_modal_verbs:
                avg_number_of_non_modal_verbs = self._feature_extractor.get_top_level().\
                    get_average_number_of_non_modal_verbs(
                    utterances=[utterance])
                if X_number_of_non_modal_verbs is None:
                    X_number_of_non_modal_verbs = []
                X_number_of_non_modal_verbs.append(avg_number_of_non_modal_verbs)

            if include_number_of_wh_words:
                avg_number_of_wh_words = self._feature_extractor.get_top_level().get_average_number_of_wh_words(
                    utterances=[utterance])
                if X_number_of_wh_words is None:
                    X_number_of_wh_words = []
                X_number_of_wh_words.append(avg_number_of_wh_words)

            X_numerical = self._feature_extractor.get_top_level().create_numerical_features(
                X_we=X_we,
                X_sentiment=X_sentiment,
                X_utt_length=X_utt_length,
                X_number_of_slots=X_number_of_slots,
                X_number_of_non_modal_verbs=X_number_of_non_modal_verbs,
                X_number_of_wh_words=X_number_of_wh_words)

            if X_tfidf is not None and X_numerical is not None:
                training_instance = scipy.sparse.hstack((X_tfidf, X_numerical), format='csr')
            elif X_tfidf is not None:
                training_instance = X_tfidf
            else:
                training_instance = X_numerical

            #training_instance = X_tfidf

            pred = top_level_trained_model.predict(training_instance)
            pred = [self._idx2tag.get_top_level()[idx] for idx in pred]

            level_info.set_top_level(pred)

        if self._classification_level == ClassificationLevelConfig.BOTTOM_LEVEL or self._classification_level == \
                ClassificationLevelConfig.TWO_LEVEL:
            include_avg_word_embeddings = False
            include_sentiment = False
            include_utt_length = False
            include_number_of_slots = False
            include_number_of_non_modal_verbs = False
            include_number_of_wh_words = False

            # Create the feature vector.
            text_feature_vector = self._feature_extractor.get_bottom_level().create_features_vector(
                utterances=norm_utterances, index=len(norm_utterances) - 1,
                include_surrounding=False,
                include_unigrams=True,
                include_tag=True,
                include_pos=True,
                include_dep=False,
                include_tag_unigrams=False,
                include_pos_unigrams=True,
                include_dep_unigrams=False,
                include_avg_word_embeddings=include_avg_word_embeddings,
                include_sentiment=include_sentiment,
                include_utt_length=include_utt_length,
                include_number_of_slots=include_number_of_slots,
                include_number_of_non_modal_verbs=include_number_of_non_modal_verbs,
                include_number_of_wh_words=include_number_of_wh_words)

            X_tfidf = self._tokenizer.get_bottom_level().transform([';'.join(text_feature_vector)])

            X_we = None
            X_utt_length = None
            X_sentiment = None
            X_number_of_slots = None
            X_number_of_non_modal_verbs = None
            X_number_of_wh_words = None

            utterance = norm_utterances[len(norm_utterances) - 1]

            if include_avg_word_embeddings:
                we = self._feature_extractor.get_bottom_level().get_average_word_embeddings(utterances=[utterance])
                if len(we.shape) != 0:
                    if X_we is None:
                        X_we = []
                    X_we.append(we)

            if include_utt_length:
                avg_utt_length = self._feature_extractor.get_bottom_level().get_average_utt_length(
                    utterances=[utterance])
                if X_utt_length is None:
                    X_utt_length = []
                X_utt_length.append(avg_utt_length)

            if include_sentiment:
                avg_sentiment = self._feature_extractor.get_bottom_level().get_average_sentiment(utterances=[utterance])
                if X_sentiment is None:
                    X_sentiment = []
                X_sentiment.append(avg_sentiment)

            if include_number_of_slots:
                avg_number_of_slots = self._feature_extractor.get_bottom_level().get_average_number_of_slots(
                    utterances=[utterance])
                if X_number_of_slots is None:
                    X_number_of_slots = []
                X_number_of_slots.append(avg_number_of_slots)

            if include_number_of_non_modal_verbs:
                avg_number_of_non_modal_verbs = self._feature_extractor.get_bottom_level().\
                    get_average_number_of_non_modal_verbs(
                    utterances=[utterance])
                if X_number_of_non_modal_verbs is None:
                    X_number_of_non_modal_verbs = []
                X_number_of_non_modal_verbs.append(avg_number_of_non_modal_verbs)

            if include_number_of_wh_words:
                avg_number_of_wh_words = self._feature_extractor.get_bottom_level().get_average_number_of_wh_words(
                    utterances=[utterance])
                if X_number_of_wh_words is None:
                    X_number_of_wh_words = []
                X_number_of_wh_words.append(avg_number_of_wh_words)

            X_numerical = self._feature_extractor.get_bottom_level().create_numerical_features(
                X_we=X_we,
                X_sentiment=X_sentiment,
                X_utt_length=X_utt_length,
                X_number_of_slots=X_number_of_slots,
                X_number_of_non_modal_verbs=X_number_of_non_modal_verbs,
                X_number_of_wh_words=X_number_of_wh_words)

            if X_tfidf is not None and X_numerical is not None:
                training_instance = scipy.sparse.hstack((X_tfidf, X_numerical), format='csr')
            elif X_tfidf is not None:
                training_instance = X_tfidf
            else:
                training_instance = X_numerical

            #training_instance = X_tfidf

            pred = bottom_level_trained_model.predict(training_instance)
            pred = [self._idx2tag.get_bottom_level()[idx] for idx in pred]

            level_info.set_bottom_level(pred)

        return level_info

    def _get_train_no_split(self):
        level_info = Level()

        data = self._get_data()

        if self._classification_level == ClassificationLevelConfig.TOP_LEVEL or self._classification_level == \
                ClassificationLevelConfig.TWO_LEVEL:
            subject_name_by_index, subject_name_by_sequence, X_raw, y_raw, y_raw_sequence, CLASSES, X_utterances, X, \
            y = data.get_top_level()

            try:
                setup_idx = self._tag2idx.get_top_level()['setup']
            except ValueError:
                setup_idx = -1

            try:
                conclusion_idx = self._tag2idx.get_top_level()['conclusion']
            except ValueError:
                conclusion_idx = -1

            X_train = []
            y_train = []
            X_train_utt = []
            for inst in [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 5, 6, 7, 8, 9]:
                for span in subject_name_by_index[inst]:
                    for utt in X_utterances[span[0]:(span[0] + len(span))]:
                        X_train_utt.append(utt)
                    if X_train == []:
                        X_train = X[span]
                        y_train = y[span].reshape(-1, 1)
                        continue
                    X_train = scipy.sparse.vstack((X_train, X[span]), format='csr')
                    y_train = scipy.sparse.vstack((csr_matrix(y_train), csr_matrix(y[span].reshape(-1, 1))),
                                                  format='csr')

            level_info.set_top_level([(None, None, \
                                       X_train, y_train.toarray().reshape(y_train.shape[0], ),
                                       None, None, None, setup_idx, conclusion_idx)])

        if self._classification_level == ClassificationLevelConfig.BOTTOM_LEVEL or self._classification_level == \
                ClassificationLevelConfig.TWO_LEVEL:
            subject_name_by_index, subject_name_by_sequence, X_raw, y_raw, y_raw_sequence, CLASSES, X_utterances, X, \
            y = data.get_bottom_level()

            try:
                setup_idx = self._tag2idx.get_top_level()['setup']
            except ValueError:
                setup_idx = -1

            try:
                conclusion_idx = self._tag2idx.get_top_level()['conclusion']
            except ValueError:
                conclusion_idx = -1

            X_train = []
            y_train = []
            X_train_utt = []
            for inst in [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 5, 6, 7, 8, 9]:
                for span in subject_name_by_index[inst]:
                    for utt in X_utterances[span[0]:(span[0] + len(span))]:
                        X_train_utt.append(utt)
                    if X_train == []:
                        X_train = X[span]
                        y_train = y[span].reshape(-1, 1)
                        continue
                    X_train = scipy.sparse.vstack((X_train, X[span]), format='csr')
                    y_train = scipy.sparse.vstack((csr_matrix(y_train), csr_matrix(y[span].reshape(-1, 1))),
                                                  format='csr')

            level_info.set_bottom_level([(None, None, \
                                          X_train, y_train.toarray().reshape(y_train.shape[0], ),
                                          None, None, None, setup_idx, conclusion_idx)])

        return level_info

    def _get_single_train_test_split(self):
        data = self._get_data()

        kfold = KFold(n_splits=2, shuffle=True, random_state=7)
        if data.get_top_level():
            total_subjects = len(data.get_top_level()[
                                     0])  # both top and bottom subject name by index will have 16 subjects (doesn't
            # matter which one to use here).
        else:
            total_subjects = len(data.get_bottom_level()[0])

        X_p = np.zeros((total_subjects,))
        y_p = np.zeros((total_subjects,))

        # if k_cross_validation=2 this will loop twice, but you just need the split of the first iteration as a user of
        # this class.
        kfolddata = []
        for train, test in kfold.split(X_p, y_p):
            level_info = Level()
            if data.get_top_level():
                subject_name_by_index, subject_name_by_sequence, X_raw, y_raw, y_raw_sequence, CLASSES, X_utterances, \
                X, y = data.get_top_level()

                try:
                    setup_idx = self._tag2idx.get_top_level()['setup']
                except ValueError:
                    setup_idx = -1

                try:
                    conclusion_idx = self._tag2idx.get_top_level()['conclusion']
                except ValueError:
                    conclusion_idx = -1

                X_train = []
                y_train = []
                X_test = []
                y_test = []

                X_train_utt = []
                X_test_utt = []

                y_test_seq_spans = []

                for inst in train:
                    for span in subject_name_by_index[inst + 5]:
                        for utt in X_utterances[span[0]:(span[0] + len(span))]:
                            X_train_utt.append(utt)
                        if X_train == []:
                            X_train = X[span]
                            y_train = y[span].reshape(-1, 1)
                        else:
                            X_train = scipy.sparse.vstack((X_train, X[span]),
                                                          format='csr')
                            y_train = scipy.sparse.vstack((csr_matrix(y_train),
                                                           csr_matrix(
                                                               y[span].reshape(-1, 1))), format='csr')
                curr_idx = 0
                for inst in test:
                    span = subject_name_by_index[inst + 5][0]
                    for utt in X_utterances[span[0]:(span[0] + len(span))]:
                        X_test_utt.append(utt)
                    if X_test == []:
                        X_test = X[span]
                        y_test = y[span].reshape(-1, 1)
                    else:
                        X_test = scipy.sparse.vstack((X_test, X[span]), format='csr')
                        y_test = scipy.sparse.vstack((csr_matrix(y_test),
                                                      csr_matrix(y[span].reshape(-1, 1))), format='csr')

                    end_span = span[0] + len(span)
                    for span in subject_name_by_sequence[inst + 5]:
                        next_idx = curr_idx + len(span)
                        y_test_seq_spans.append(range(curr_idx, next_idx))
                        curr_idx = next_idx
                        if end_span == (span[0] + len(span)):
                            break
                level_info.set_top_level((train, test,
                                          X_train, y_train.toarray().reshape(y_train.shape[0], ),
                                          X_test, y_test.toarray().reshape(y_test.shape[0], ),
                                          y_test_seq_spans, setup_idx, conclusion_idx))

            if data.get_bottom_level():
                subject_name_by_index, subject_name_by_sequence, X_raw, y_raw, y_raw_sequence, CLASSES, X_utterances, \
                X, y = data.get_bottom_level()

                try:
                    setup_idx = self._tag2idx.get_top_level()['setup']
                except ValueError:
                    setup_idx = -1

                try:
                    conclusion_idx = self._tag2idx.get_top_level()['conclusion']
                except ValueError:
                    conclusion_idx = -1

                X_train = []
                y_train = []
                X_test = []
                y_test = []

                X_train_utt = []
                X_test_utt = []

                y_test_seq_spans = []

                for inst in train:
                    for span in subject_name_by_index[inst + 5]:
                        print("PROCESSING subject", inst + 5, "with current span", span)
                        if not start_span:
                            start_span = span[0]
                        for utt in X_utterances[span[0]:(span[0] + len(span))]:
                            X_train_utt.append(utt)
                        if X_train == []:
                            X_train = X[span]
                            y_train = y[span].reshape(-1, 1)
                        else:
                            X_train = scipy.sparse.vstack((X_train, X[span]),
                                                          format='csr')
                            y_train = scipy.sparse.vstack((csr_matrix(y_train),
                                                           csr_matrix(
                                                               y[span].reshape(-1, 1))), format='csr')
                curr_idx = 0
                for inst in test:
                    span = subject_name_by_index[inst + 5][0]
                    for utt in X_utterances[span[0]:(span[0] + len(span))]:
                        X_test_utt.append(utt)
                    if X_test == []:
                        X_test = X[span]
                        y_test = y[span].reshape(-1, 1)
                    else:
                        X_test = scipy.sparse.vstack((X_test, X[span]), format='csr')
                        y_test = scipy.sparse.vstack((csr_matrix(y_test),
                                                      csr_matrix(y[span].reshape(-1, 1))), format='csr')

                    for span in subject_name_by_sequence[inst + 5]:
                        next_idx = curr_idx + len(span)
                        y_test_seq_spans.append(range(curr_idx, next_idx))
                        curr_idx = next_idx
                        if end_span == (span[0] + len(span)):
                            break
                level_info.set_bottom_level((train, test,
                                             X_train, y_train.toarray().reshape(y_train.shape[0], ),
                                             X_test, y_test.toarray().reshape(y_test.shape[0], ),
                                             y_test_seq_spans, setup_idx, conclusion_idx))
            kfolddata.append(level_info)

            # just go through one itereation of the loop
            return kfolddata

    def _get_cross_validation_train_test_split(self):
        data = self._get_data()

        kfold = KFold(n_splits=self._k_cross_validation, shuffle=True, random_state=7)
        if data.get_top_level():
            total_subjects = len(data.get_top_level()[
                                     0])  # both top and bottom subject name by index will have 16 subjects (doesn't
            # matter which one to use here).
        else:
            total_subjects = len(data.get_bottom_level()[0])

        X_p = np.zeros((total_subjects,))
        y_p = np.zeros((total_subjects,))

        # if k_cross_validation=2 this will loop twice, but you just need the split of the first iteration as a user of
        # this class.
        kfolddata = []
        for train, test in kfold.split(X_p, y_p):
            level_info = Level()
            if data.get_top_level():
                subject_name_by_index, subject_name_by_sequence, X_raw, y_raw, y_raw_sequence, CLASSES, X_utterances, \
                X, y = data.get_top_level()

                try:
                    setup_idx = self._tag2idx.get_top_level()['setup']
                except ValueError:
                    setup_idx = -1

                try:
                    conclusion_idx = self._tag2idx.get_top_level()['conclusion']
                except ValueError:
                    conclusion_idx = -1

                X_train = []
                y_train = []
                X_test = []
                y_test = []

                X_train_utt = []
                X_test_utt = []

                y_test_seq_spans = []

                for inst in train:
                    for span in subject_name_by_index[inst + 5]:
                        for utt in X_utterances[span[0]:(span[0] + len(span))]:
                            X_train_utt.append(utt)
                        if X_train == []:
                            X_train = X[span]
                            y_train = y[span].reshape(-1, 1)
                        else:
                            X_train = scipy.sparse.vstack((X_train, X[span]),
                                                          format='csr')
                            y_train = scipy.sparse.vstack((csr_matrix(y_train),
                                                           csr_matrix(
                                                               y[span].reshape(-1, 1))), format='csr')
                curr_idx = 0
                for inst in test:
                    span = subject_name_by_index[inst + 5][0]
                    for utt in X_utterances[span[0]:(span[0] + len(span))]:
                        X_test_utt.append(utt)
                    if X_test == []:
                        X_test = X[span]
                        y_test = y[span].reshape(-1, 1)
                    else:
                        X_test = scipy.sparse.vstack((X_test, X[span]), format='csr')
                        y_test = scipy.sparse.vstack((csr_matrix(y_test),
                                                      csr_matrix(y[span].reshape(-1, 1))), format='csr')

                    end_span = span[0] + len(span)
                    for span in subject_name_by_sequence[inst + 5]:
                        next_idx = curr_idx + len(span)
                        y_test_seq_spans.append(range(curr_idx, next_idx))
                        curr_idx = next_idx
                        if end_span == (span[0] + len(span)):
                            break
                level_info.set_top_level((train, test,
                                          X_train, y_train.toarray().reshape(y_train.shape[0], ),
                                          X_test, y_test.toarray().reshape(y_test.shape[0], ),
                                          y_test_seq_spans, setup_idx, conclusion_idx))

            if data.get_bottom_level():
                subject_name_by_index, subject_name_by_sequence, X_raw, y_raw, y_raw_sequence, CLASSES, X_utterances, \
                X, y = data.get_bottom_level()

                try:
                    setup_idx = self._tag2idx.get_top_level()['setup']
                except ValueError:
                    setup_idx = -1

                try:
                    conclusion_idx = self._tag2idx.get_top_level()['conclusion']
                except ValueError:
                    conclusion_idx = -1

                X_train = []
                y_train = []
                X_test = []
                y_test = []

                X_train_utt = []
                X_test_utt = []

                y_test_seq_spans = []

                for inst in train:
                    for span in subject_name_by_index[inst + 5]:
                        for utt in X_utterances[span[0]:(span[0] + len(span))]:
                            X_train_utt.append(utt)
                        if X_train == []:
                            X_train = X[span]
                            y_train = y[span].reshape(-1, 1)
                        else:
                            X_train = scipy.sparse.vstack((X_train, X[span]),
                                                          format='csr')
                            y_train = scipy.sparse.vstack((csr_matrix(y_train),
                                                           csr_matrix(
                                                               y[span].reshape(-1, 1))), format='csr')
                curr_idx = 0
                for inst in test:
                    span = subject_name_by_index[inst + 5][0]
                    for utt in X_utterances[span[0]:(span[0] + len(span))]:
                        X_test_utt.append(utt)
                    if X_test == []:
                        X_test = X[span]
                        y_test = y[span].reshape(-1, 1)
                    else:
                        X_test = scipy.sparse.vstack((X_test, X[span]), format='csr')
                        y_test = scipy.sparse.vstack((csr_matrix(y_test),
                                                      csr_matrix(y[span].reshape(-1, 1))), format='csr')

                    end_span = span[0] + len(span)
                    for span in subject_name_by_sequence[inst + 5]:
                        next_idx = curr_idx + len(span)
                        y_test_seq_spans.append(range(curr_idx, next_idx))
                        curr_idx = next_idx
                        if end_span == (span[0] + len(span)):
                            break
                level_info.set_bottom_level((train, test,
                                             X_train, y_train.toarray().reshape(y_train.shape[0], ),
                                             X_test, y_test.toarray().reshape(y_test.shape[0], ),
                                             y_test_seq_spans, setup_idx, conclusion_idx))
            kfolddata.append(level_info)

        return kfolddata

    def _get_data(self):
        level_info = Level()

        if self._classification_level == ClassificationLevelConfig.TOP_LEVEL or self._classification_level == \
                ClassificationLevelConfig.TWO_LEVEL:
            print("Extracting top level data...")
            feature_builder = BOWFeatureVectors(feature_extractor=self._feature_extractor.get_top_level())
            subject_name_by_index, subject_name_by_sequence, X_raw, y_raw, y_raw_sequence, CLASSES, X_utterances, X, \
            y, tfidf, tag2idx, idx2tag = \
                feature_builder.extract(
                    corpus_path=self._corpus_path,
                    tokenize=self._use_tokenizer,
                    include_setup=True,
                    include_request=True,
                    include_conclusion=True,
                    include_surrounding=False,
                    include_unigrams=True,
                    include_tag=True,
                    include_pos=True,
                    include_dep=False,
                    include_tag_unigrams=False,
                    include_pos_unigrams=True,
                    include_dep_unigrams=False,
                    include_avg_word_embeddings=False,
                    include_sentiment=False,
                    include_utt_length=False,
                    include_number_of_slots=False,
                    include_number_of_non_modal_verbs=False,
                    include_number_of_wh_words=False,
                    IGNORE_CLASSES=['appearance', 'big high level question'],
                    MERGE_CLASSES=['createvis', 'modifyvis', 'factbased', 'preference', 'winmgmt', 'clarification'],
                    is_corpus_json=self._use_paraphrasing,
                    total_versions=self._total_versions)

            print("Loaded",self._name.get_top_level(),"features", X.shape, y.shape)
            self._tokenizer.set_top_level(tfidf)
            self._tag2idx.set_top_level(tag2idx)
            self._idx2tag.set_top_level(idx2tag)
            self._classes.set_top_level(CLASSES)
            level_info.set_top_level((subject_name_by_index, subject_name_by_sequence, X_raw, y_raw, y_raw_sequence,
                                      CLASSES, X_utterances, X, y))

        if self._classification_level == ClassificationLevelConfig.BOTTOM_LEVEL or self._classification_level == \
                ClassificationLevelConfig.TWO_LEVEL:
            print("Extracting bottom level data...")
            feature_builder = BOWFeatureVectors(feature_extractor=self._feature_extractor.get_bottom_level())
            subject_name_by_index, subject_name_by_sequence, X_raw, y_raw, y_raw_sequence, CLASSES, X_utterances, X, \
            y, tfidf, tag2idx, idx2tag = \
                feature_builder.extract(
                    corpus_path=self._corpus_path,
                    tokenize=self._use_tokenizer,
                    include_setup=False,
                    include_request=True,
                    include_conclusion=False,
                    include_surrounding=False,
                    include_unigrams=True,
                    include_tag=True,
                    include_pos=True,
                    include_dep=False,
                    include_tag_unigrams=False,
                    include_pos_unigrams=True,
                    include_dep_unigrams=False,
                    include_avg_word_embeddings=False,
                    include_sentiment=False,
                    include_utt_length=False,
                    include_number_of_slots=False,
                    include_number_of_non_modal_verbs=False,
                    include_number_of_wh_words=False,
                    IGNORE_CLASSES=['appearance', 'big high level question'],
                    MERGE_CLASSES=['createvis', 'modifyvis'],
                    is_corpus_json=self._use_paraphrasing,
                    total_versions=self._total_versions)

            print("Loaded",self._name.get_bottom_level(),"features", X.shape, y.shape)
            self._tokenizer.set_bottom_level(tfidf)
            self._tag2idx.set_bottom_level(tag2idx)
            self._idx2tag.set_bottom_level(idx2tag)
            self._classes.set_bottom_level(CLASSES)
            level_info.set_bottom_level((subject_name_by_index, subject_name_by_sequence, X_raw, y_raw, y_raw_sequence,
                                         CLASSES, X_utterances, X, y))

        return level_info

    def get_model_architecture(self, words, tags, which_level):
        return BalancedBaggingClassifier(n_estimators=self._iterations,
                                         random_state=0, n_jobs=1)
