import copy
import datetime
from abc import abstractmethod
from collections import Counter

import numpy as np
import scipy
from keras.preprocessing.sequence import pad_sequences
from keras.utils import np_utils
from keras.wrappers.scikit_learn import KerasClassifier
from scipy.sparse.csr import csr_matrix
from sklearn.model_selection import KFold
from keras.callbacks import EarlyStopping

from .dialogue_act_model import DialogueActModel
from .level import Level
from .utils import ClassificationLevelConfig, UseEmbeddingConfig
from ..corpus_feature_extractor.context_based_feature_vectors import ContextBasedFeatureVectors
from ..corpus_feature_extractor.request_based_feature_vectors import RequestBasedFeatureVectors
from ..corpus_feature_extractor.sequence_feature_vectors import SequenceFeatureVectors
from .sequence_metrics import SequenceMetrics

'''LSTMBASE model:
	init:
		1. Note: the name should be "BAGC"
	train: 
		1. Either you can train top level classifier (classification_level=ClassificationLevelConfig.TOP_LEVEL) 
		which means to classify as request vs nonrequest (i.e.,'merged' or 'setup' or 'conclusion') or as bottom level 
		classifier (ClassificationLevelConfig.BOTTOM_LEVEL) (i.e., classify as 'createvis', 'modifyvis', 
		'preferencebased', 'factbased', 'clarification', 'winmgmt') or two level classification 
		(ClassificationLevelConfig.TWO_LEVEL)

		2. You can train using all the training data (i.e., k_cross_validation=-1), or a single train and test split 
		(k_cross_validation=1) or set to any larger positive integer (i.e., k_cross_validation=5 generates 
		5-fold cross validation)
		Note: splits are across the 16 subjects, not the actual utterances themselves (i.e., 
			one sample 5-fold split could be: training=[1,2,3,4,5,6,7,8,9,10,11],test=[12,13,14,15,16])

		3. The use_paraphrasing=True indicates using augmented corpus with AUGX multiplier = total_versions.
		Note: total_versions=10 means you have 10 X more subjects (i.e., 160 subjects).

		4. The embedding_model_path is the path to a word embedding weight matrix. Note that 
		'word2vec.100d.chicagocrimevis.wv.pkl' is the custom trained word embedding on chicago crime vis text,
		but you could set it to standard pre-trained word embedding model, or even set it to None (in the case
		of deep learnign model ONLY) to allow the model to learn it while training.

		5. The use_tokenizer=True flag means to use the rule-based semantic slot filling custom built for the 
		chicagocrimevis corpus. Leveraging it will tokenize all kinds of mutli-expression words (e.g., "river north" 
		instead of "river", "north").
'''


class LSTMBASEModel(DialogueActModel):
    '''
    name: the name of the model (string). This is required.
    copy_model: if you want to copy a different model into this current instance or otherwise None (optional)
    is_sequence_model: BILSTMCRF is performing sequence tagging (True) while the other keras models are not (False).
    train_with_categorical_labels: The CONVFILTER model requires categorical labels while training (True) and other
    keras models do not (False).
    '''

    def __init__(self, name, is_sequence_model):
        super().__init__(name=name, is_sequence_model=is_sequence_model)

    '''
    Evaluate the model on k_cross_validation total folds.
    classification_level: Either classify top level (conclusion, merged, setup), 
        bottom level (merged, clarification, fact-based, winmgmt, etc.), 
        or two level (conclusion, <merged>, setup) where <merged> is either
        merged (meaning createvis+modifyvis) or clarification, or winmgmt, etc.
    k_cross_validation: total number of folds for k-fold cross validation.
    use_paraphrasing: use data augmented corpus
    total_versions: sets the AUGX parameter
    embedding_type: either use the crime embeddings (UseEmbeddingConfig.USE_CRIME_EMBEDDING), 
        a pre-trained GlOve model (UseEmbeddingConfig.PRETRAINED_EMBEDDING), 
        or let the keras model train its own embeddings (UseEmbeddingConfig.USE_NO_EMBEDDING).
    use_tokenizer: leverage our own custom built semantic slot filler in SpaCy to tokenize 
        (e.g., "river north" instead of incorrectly tokenizing as "river" "north")
    overwrite: overwrite an existing saved model (True) or just load the existing one instead of training (False)
    max_sequence_length: cut-off for the total number of words in an utterance.
    max_queries: Used by BILSTMCRF which defines max number of utterances allowed in a given context.
    '''

    '''
    Train the model on k_cross_validation total folds.
    classification_level: Either classify top level (conclusion, merged, setup), 
        bottom level (merged, clarification, fact-based, winmgmt, etc.), 
        or two level (conclusion, <merged>, setup) where <merged> is either
        merged (meaning createvis+modifyvis) or clarification, or winmgmt, etc.
    k_cross_validation: total number of folds for k-fold cross validation.
    use_paraphrasing: use data augmented corpus
    total_versions: sets the AUGX parameter
    embedding_type: either use the crime embeddings (UseEmbeddingConfig.USE_CRIME_EMBEDDING), 
        a pre-trained GlOve model (UseEmbeddingConfig.PRETRAINED_EMBEDDING), 
        or let the keras model train its own embeddings (UseEmbeddingConfig.USE_NO_EMBEDDING).
    use_tokenizer: leverage our own custom built semantic slot filler in SpaCy to tokenize 
        (e.g., "river north" instead of incorrectly tokenizing as "river" "north")
    overwrite: overwrite an existing saved model (True) or just load the existing one instead of training (False)
    max_sequence_length: cut-off for the total number of words in an utterance.
    max_queries: Used by BILSTMCRF which defines max number of utterances allowed in a given context.
    '''

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

                for i, l in enumerate(self.get_model_architecture(
                        words=None, tags=None, which_level=ClassificationLevelConfig.TOP_LEVEL).layers):
                    print(f'layer {i}: {l}')
                    print(f'has input mask: {l.input_mask}')
                    print(f'has output mask: {l.output_mask}')

                class_weight = self.get_class_weight(y_train)
                print("Class weights", class_weight)

                top_trained_model = self.load_model(which_level=ClassificationLevelConfig.TOP_LEVEL, subjects=test,
                                                    fold=fold)

                if top_trained_model:
                    print("Found existing model for X_train", X_train.shape, "y_train", y_train.shape, Counter(y_train),
                          "X_test", X_test.shape, "y_test", y_test.shape, Counter(y_test), "Classes",
                          self._tag2idx.get_top_level())
                else:
                    top_trained_model = KerasClassifier(
                        build_fn=self.get_model_architecture, words=None, tags=None,
                        which_level=ClassificationLevelConfig.TOP_LEVEL,
                        epochs=self._iterations, batch_size=300, verbose=True)

                    print("No existing model for X_train", X_train.shape, "y_train", y_train.shape, Counter(y_train),
                          "X_test", X_test.shape, "y_test", y_test.shape, Counter(y_test), "Classes",
                          self._tag2idx.get_top_level())

                    start_time = datetime.datetime.now()

                    top_trained_model.fit(
                        X_train,
                        np_utils.to_categorical(y_train),
                        validation_data=(X_test, np_utils.to_categorical(y_test)),
                        batch_size=300,
                        epochs=self._iterations,
                        verbose=1,
                        class_weight=None,
                        callbacks = [SequenceMetrics(self._idx2tag.get_top_level(), num_inputs=1),
                                     EarlyStopping(
                                         monitor='val_f1', patience=4, restore_best_weights=True, mode='max')]
                    )

                    end_time = datetime.datetime.now()
                    print("TIME DURATION", end_time - start_time)
                    self.save_model(
                        which_level=ClassificationLevelConfig.TOP_LEVEL, trained_model=top_trained_model, subjects=test,
                        fold=fold)

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

                    y_pred_norm.set_top_level(
                        DialogueActModel.adjust_request_if_missing_or_too_many_in_context(
                            y=y_pred_norm.get_top_level(), tag2idx=self._tag2idx.get_top_level(), requests=requests,
                            setup_key=top_level_setup_idx, conclusion_key=top_level_conclusion_idx,
                            replace_key=top_level_setup_idx))

                    print("\n\nTop Level Classifier: " + self._name.get_top_level() + ", Fold: " + str(fold + 1))
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

                class_weight = self.get_class_weight(y_train)
                print("Class weights", class_weight)

                bottom_trained_model = self.load_model(which_level=ClassificationLevelConfig.BOTTOM_LEVEL,
                                                       subjects=test, fold=fold)

                if bottom_trained_model:
                    print("Found existing model for X_train", X_train.shape, "y_train", y_train.shape, Counter(y_train),
                          "X_test", X_test.shape, "y_test", y_test.shape, Counter(y_test), "Classes",
                          self._tag2idx.get_bottom_level())

                else:
                    bottom_trained_model = KerasClassifier(build_fn=self.get_model_architecture, words=None,
                                                           tags=None,
                                                           which_level=ClassificationLevelConfig.BOTTOM_LEVEL,
                                                           epochs=self._iterations, batch_size=300, verbose=True)

                    print("No existing model for X_train", X_train.shape, "y_train", y_train.shape, Counter(y_train),
                          "X_test", X_test.shape, "y_test", y_test.shape, Counter(y_test), "Classes",
                          self._tag2idx.get_bottom_level())

                    start_time = datetime.datetime.now()
                    bottom_trained_model.fit(
                        X_train,
                        np_utils.to_categorical(y_train),
                        validation_data=(X_test, np_utils.to_categorical(y_test)),
                        batch_size=300,
                        epochs=self._iterations,
                        verbose=1,
                        class_weight=None,
                        callbacks = [SequenceMetrics(self._idx2tag.get_bottom_level(), num_inputs=1),
                                     EarlyStopping(
                                         monitor='val_f1', patience=4, restore_best_weights=True, mode='max')]
                    )

                    end_time = datetime.datetime.now()
                    print("TIME DURATION", end_time - start_time)
                    self.save_model(subjects=test,
                                    which_level=ClassificationLevelConfig.BOTTOM_LEVEL,
                                    trained_model=bottom_trained_model, fold=fold)

                if evaluate:
                    y_pred = bottom_trained_model.predict(X_test)

                    y_test_norm.set_bottom_level(DialogueActModel.transform_to_sequence(y_test_seq_spans, y_test))

                    y_pred_norm.set_bottom_level(DialogueActModel.transform_to_sequence(y_test_seq_spans, y_pred))

                    requests = np.unique(
                        [item for sublist in y_test_norm.get_bottom_level() \
                         for item in sublist])

                    print("\n\nBottom Level Classifier: " + self._name.get_bottom_level() + ", Fold: " + str(fold + 1))
                    bottom_level_performance = self._compute_performance(
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
                        self._name.get_bottom_level() + ", Fold: " + str(
                            fold + 1))
                    two_level_performance = \
                        self._compute_performance(
                            name='two_level_'+self._name.get_top_level().split('_')[-1],
                            y_test=y_test_requests, y_pred=y_pred_requests,
                            idx2tag=merged_idx2tag,
                            filter_class_labels=['PAD', 'UNK', 'merged', 'conclusion'],
                            performance_dict=two_level_performance)

        self._print_performance(fold=fold + 1, performance_dict=top_level_performance, name=self._name.get_top_level())
        self._print_performance(fold=fold + 1, performance_dict=bottom_level_performance,
                                name=self._name.get_bottom_level())
        self._print_performance(fold=fold + 1, performance_dict=two_level_performance,
                                name=self._name.get_top_level() + ", " + self._name.get_bottom_level())

    '''
    Leverage the trained model to predict a list of utterances.
    Note: Each utterance must be tokenized via SpaCy and hence a SpaCy object (e.g., Doc object).
    '''

    def predict(self, top_level_trained_model, bottom_level_trained_model, context_utterances):
        start_idx = 0
        if len(context_utterances) > self._max_queries:
            start_idx = -1 * self._max_queries
        norm_utterances = context_utterances[start_idx:]

        # Create the feature vector.
        level_info = Level()
        if self._classification_level == ClassificationLevelConfig.TOP_LEVEL or self._classification_level == \
                ClassificationLevelConfig.TWO_LEVEL:
            feature_vector = self._feature_extractor.get_top_level().create_features_vector(utterances=norm_utterances,
                                                                                index=len(norm_utterances) - 1,
                                                                                include_surrounding=False,
                                                                                include_unigrams=True,
                                                                                include_tag=False,
                                                                                include_pos=False,
                                                                                include_dep=False,
                                                                                include_tag_unigrams=False,
                                                                                include_pos_unigrams=False,
                                                                                include_dep_unigrams=False,
                                                                                include_avg_word_embeddings=
                                                                                False,
                                                                                include_sentiment=False,
                                                                                include_utt_length=False,
                                                                                include_number_of_slots=
                                                                                False,
                                                                                include_number_of_non_modal_verbs=False,
                                                                                include_number_of_wh_words=False)

            training_instance = pad_sequences(
                self._tokenizer.get_top_level().texts_to_sequences([';'.join(feature_vector)]),
                self._max_sequence_length)
            pred = top_level_trained_model.predict(training_instance)
            pred = [self._idx2tag.get_top_level()[i] for i in pred]
            # pred=self._label_encoder.get_top_level().inverse_transform(pred)
            level_info.set_top_level(pred)

        if self._classification_level == ClassificationLevelConfig.BOTTOM_LEVEL or self._classification_level == \
                ClassificationLevelConfig.TWO_LEVEL:
            feature_vector = self._feature_extractor.get_bottom_level().create_features_vector(
                utterances=norm_utterances, index=len(norm_utterances) - 1,
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
                include_number_of_non_modal_verbs=False,
                include_number_of_wh_words=False)

            training_instance = pad_sequences(
                self._tokenizer.get_bottom_level().texts_to_sequences([';'.join(feature_vector)]),
                self._max_sequence_length)
            pred = bottom_level_trained_model.predict(training_instance)
            # pred=self._label_encoder.get_bottom_level().inverse_transform(pred)
            pred = [self._idx2tag.get_bottom_level()[i] for i in pred]
            level_info.set_bottom_level(pred)

        return level_info

    '''
    The description below applies to the next 3 methods (e.g., _get_train_no_split, _get_single_train_test_split
    and _get_cross_validation_train_test_split
    Put aside for a moment the cross validation piece. Here are the dimensions would be expected disregarding cross 
    validation.

    N (the total subjects) = TOTAL_VERSIONS * 16 subjects (e.g., 160 subjects when 10 versions are generated by 
    paraphraser).
    C (the total contexts) = 4400 when TOTAL_VERSIONS=10

    X: is the index representation of all N utterances produced by paraphraser.
    Dimenions are N X 40 since MAX_SEQ_LEN=40.

    y: is the index representation of all N labels, one for each utterance produced by paraphraser.
    Dimensions are N X 1.

    X_utterances: the actual N utterances produced.

    subject_name_by_index: For each of the 16 subjects (subject 5 through subject 20), there are TOTAL_VERSIONS 
    associated ranges.
    Each range represents the start through end indices for each of the TOTAL_VERSIONS versions generated by the 
    paraphraser.
    (e.g., subject_name_by_index[5] contains 10 elements, each element is a range representing 1 of the 10 total 
    versions generated
    by the paraphraser, when TOTAL_VERSIONS=10). In all, total elements is therefore 16 subjects * TOTAL_VERSIONS = 160.
    Clearly, if you sum up all the range lengths, that will equal the total utterances N.

    subject_name_by_sequence: For each of the 16 subjects (subject 5 through subject 20), there are range elements for 
    each
    annotated context. X_utterances[subject_name_by_sequence][5][0] for example produces the first context for 
    subject 5.
    When TOTAL_VERSIONS=10, ther are approximately C=4400 total contexts and clearly if you sum up all the range 
    elements in
    this dictionary, it will be N.

    The LSTM, BiLSTM, and LSTM-CNN models simply require the index representation of each context i.e., (X,y) or 
    equivalently, (X_train, y_train). Dimensions are N X 40. These are found in X_train, X_test, y_train, and y_test:

    Xtest -> 10 X 114 X 20

                0		1		2		3		4		5		6		7		8		9

    Cntxt 1		U0		U1		.		.		.										U9
    Cntxt 2		U0		U1		.		.		.										U9
    .
    .
    .
    Cntxt114	U0		U1		.		.		.										U9



    ytest -> 10 X 114 X 1
                0		1		2		3		4		5		6		7		8		9

    Cntxt 1		L0		L1		.		.		.										L9
    Cntxt 2		L0		L1		.		.		.										L9
    .
    .
    .
    Cntxt114	L0		L1		.		.		.										L9

    The BiLSTMCRF expects a single instance to be an array of size 20 (max number of utterances in a given context).
    This is represented by X_train_seq:

    X_train_seq[0] is the first utterance for each of the total contexts C (e.g., C=4400 contexts when 
    TOTAL_VERSIONS=10).
    X_train_seq[1] is the second utterance for each of the C contexts.
    .
    .
    .
    X_train_seq[19] is the final utterance for each of the C contexts.

    In other words, the shape of X_train_seq is 20 X 4400 X 40. Also y_train_seq has shape (20 X 4400 X 1).

    For example, assuming we start counting from subject 10 through subject 9 (which is how the code has been 
    implemented), then sum of all the ranges from subject_name_by_sequence[10] through subject[20] add up to 339 
    (when paraphrasing is off). The
    first context in subject 5 consists of 3 utterances total (1 setup, 1 request, 1 conclusion). These can therefore 
    be found at
    (X_train_seq[17][339], X_train_seq[18][339], X_train_seq[19][339]) with corresponding labels 
    (y_train_seq[17][339], y_train_seq[18][339], y_train_seq[19][339]). Equivalently we can obtain using 
    (X[subject_name_by_sequence[5][0]], y[subject_name_by_sequence[5][0]]) or 
    (np.asarray(X_raw)[subject_name_by_sequence[5][0]],np.asarray(y_raw)[subject_name_by_sequence[5][0]]) or
    (X_train[subject_name_by_sequence[5][0]],y_train[subject_name_by_sequence[5][0]]) or
    np.asarray(X_utterances)[subject_name_by_sequence[5][0]].

    An important question then rises, how do you supply a training instance to this model (i.e., what is the shape)?
    You must supply the instance as a list of size 20, each element containing an 1 X 40 numpy array.

    Step 1: Need to generate context training instance for following example:
    utterances=[
        'so river north well thats pretty popular we should look at that',
        'so show me thefts in river north',
        'ok wow interesting more crime in the summer months']

    Step 2: Create spacy nlp tool that accounts for our customized named entities
    extractor = corpus_feature_extractor.CorpusFeatureExtractorUtils.\
            get_context_based_corpus_entity_extractor(\
                embedding_model_path = \
                    ModelPaths.WORD_EMBEDDING_MODELS + 'word2vec.100d.chicagocrimevis.pkl')
    nlp = extractor.get_tokenizer()

    Step 3: Iterate each utterance and obtain the appropriate one-hot representation for the neural network input.
    utterances_tokenized=[nlp(utterance) for utterance in utterances]
    encodings=[]
    for idx in range(len(utterances_tokenized)):
        feature_vector = \
            feature_extractor.create_features_vector(utterances=utterances_tokenized,index=index,\
                include_surrounding=False,\
                include_unigrams=True,\
                 include_tag=False,\
                include_pos=False,\
                include_dep=False,\
                include_tag_unigrams=False,\
                include_pos_unigrams=False,\
                include_dep_unigrams=False,\
                include_avg_word_embeddings=False,\
                include_sentiment=False,\
                include_utt_length=False,\
                include_number_of_slots=False,\
                include_number_of_non_modal_verbs=False,\
                include_number_of_wh_words=False)
        encodings.append(\
            pad_sequences(tokenizer.texts_to_sequences([';'.join(feature_vector)]),MAX_SEQ_LEN)

    Step 4: Now we have a list of 3 elements, each of shape 1 X 40. Only thing remaining is to pad
    with 17 more elements of np.zeros((1,40)) appended to the front.

    encodings = [np.zeros((1,40)) for i in enumerate(range(20-3))]

    Finally, we have the training instance representation of a single context! BTW, note that suppose if you wanted to 
    predict 3 contexts instead of just 1, you would need to pass an array of 20 elements again, but in this case, each 
    element has shape 3 X 40 instead of 1 X 40. One other thing to keep in mind, the prediction for a single instance
    takes shape of 20 X 1 X 1, each value is an integer value of either 2 (setup), 1 (merged which is same as request), 
    or 0 (conclusion), otherwise it is 3 (none). In our example, it may be [3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,2,1,0].

    Final note: When applying back k-cross validation, we note that cross validation results in folds across subjects 
    and NOT splitting of the data itself. Consider the example of 4-fold cross validation with 16 subjects. This 
    implies a fold of 4 subjects for testing and 12 subjects for training. Hence, X_train and X_test (original 
    dimentions of N X 40) will be sliced accordingly for each fold. In addition, X_train_seq (original dimensions of 
    MAX_QUERIES X C X MAX_SEQ_LEN which is 20 X 4400 X 40 when TOTAL_VERSIONS=10) will also be sliced accordingly, 
    again with splits occurring across subjects and NOT utterances directly.
    '''

    def _get_train_no_split(self):
        level_info = Level()

        data = self._get_data()

        setup_idx, conclusion_idx = -1, -1
        if self._classification_level == ClassificationLevelConfig.TOP_LEVEL or \
                self._classification_level == ClassificationLevelConfig.TWO_LEVEL:
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

            X_train_seq = []
            y_train_seq = []

            X_train_utt = []

            y_cat = np_utils.to_categorical(y)

            # index for 'PAD'
            blank_idx = 0

            curr_idx = 0
            # Note (X,y,X_raw,y_raw) all start with subject 10. On the other hand, depending on where the
            # the k cross fold split happens, this may not line up exactly the same with (X_train,y_train).
            # In other words, they could start with different subject.
            for inst in [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 5, 6, 7, 8, 9]:
                start_span = None
                for span in subject_name_by_index[inst]:
                    if not start_span:
                        start_span = span[0]
                    for utt in X_utterances[span[0]:(span[0] + len(span))]:
                        X_train_utt.append(utt)
                    if X_train == []:
                        X_train = X[span]
                        y_train = y[span].reshape(-1, 1)
                        continue
                    X_train = scipy.sparse.vstack((X_train, X[span]), format='csr')
                    y_train = scipy.sparse.vstack((csr_matrix(y_train), csr_matrix(y[span].reshape(-1, 1))),
                                                  format='csr')

            end_span = span[0] + len(span)
            from_span = start_span
            for span in subject_name_by_sequence[inst + 5]:
                next_idx = curr_idx + len(span)
                to_span = from_span + len(span)
                padding_dim = max(self._max_queries - (next_idx - curr_idx), 0)
                if padding_dim == 0:
                    curr_idx = next_idx
                    from_span = to_span
                    continue

                X_seq = X[from_span:to_span].transpose()
                X_seq_padding = csr_matrix(np.zeros((X_seq.shape[0], padding_dim)), dtype='int32')
                X_seq = scipy.sparse.hstack([X_seq_padding, X_seq], format='csr')
                if X_train_seq == []:
                    X_train_seq = X_seq
                else:
                    X_train_seq = scipy.sparse.vstack([X_train_seq, X_seq], format='csr')

                # assign y_seq to the current context labels (e.g., if context has one setup utterance, one request,
                # and one conclusion utterance, then y_seq=[0,1,2])).
                y_seq = y[from_span:to_span]

                # If y_seq=[0,1,2] then that means we need to create 17 more array elements to pad y_seq, so that we
                # reconstruct the 20 element size for a given context. So,
                # y_seq_padding=[3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3]. Hence, y_seq_padding holds 17 elements.
                y_seq_padding = np.zeros((padding_dim))
                y_seq_padding += blank_idx

                # Now we concatenate y_seq_padding and y_seq to obtain [3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,0,1,2]
                y_seq = scipy.sparse.vstack([
                    csr_matrix(y_seq_padding.reshape(y_seq_padding.shape + (1,))),
                    csr_matrix(y_seq.reshape(y_seq.shape + (1,)))], format='csr')
                if y_train_seq == []:
                    y_train_seq = y_seq
                else:
                    y_train_seq = scipy.sparse.vstack([y_train_seq, y_seq], format='csr')

                curr_idx = next_idx
                from_span = to_span
                if end_span == (span[0] + len(span)):
                    break
            X_train_seq = X_train_seq[:self._max_sequence_length * \
                                       int(X_train_seq.shape[0] / self._max_sequence_length)]
            X_train_seq_arr = []
            for idx in range(self._max_queries):
                X_train_seq_arr.append(X_train_seq[:, idx].reshape(-1, self._max_sequence_length, 1).toarray())

            y_train_seq_arr = np.asarray(y_train_seq.todense()). \
                reshape(int(y_train_seq.shape[0] / self._max_queries), self._max_queries)

            # we
            y_train_seq_arr = y_train_seq_arr.reshape(y_train_seq_arr.shape[0], y_train_seq_arr.shape[1], 1)

            if self._is_sequence_model:
                level_info.set_top_level((None, None,
                                          X_train_seq, y_train_seq, None, None, None, setup_idx, conclusion_idx))
            else:
                level_info.set_top_level((None, None,
                                          X_train, y_train.toarray().reshape(y_train.shape[0], ), None, None, None,
                                          setup_idx, conclusion_idx))

        if self._classification_level == ClassificationLevelConfig.BOTTOM_LEVEL or self._classification_level == \
                ClassificationLevelConfig.TWO_LEVEL:
            subject_name_by_index, subject_name_by_sequence, X_raw, y_raw, y_raw_sequence, CLASSES, X_utterances, X, \
            y = data.get_bottom_level()

            X_train = []
            y_train = []

            X_train_seq = []
            y_train_seq = []

            X_train_utt = []

            y_cat = np_utils.to_categorical(y)

            # index for 'PAD'
            blank_idx = 0

            curr_idx = 0
            # Note (X,y,X_raw,y_raw) all start with subject 10. On the other hand, depending on where the
            # the k cross fold split happens, this may not line up exactly the same with (X_train,y_train).
            # In other words, they could start with different subject.
            for inst in [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 5, 6, 7, 8, 9]:
                start_span = None
                for span in subject_name_by_index[inst]:
                    if not start_span:
                        start_span = span[0]
                    for utt in X_utterances[span[0]:(span[0] + len(span))]:
                        X_train_utt += utt
                    if X_train == []:
                        X_train = X[span]
                        y_train = y[span].reshape(-1, 1)
                        continue
                    X_train = scipy.sparse.vstack((X_train, X[span]), format='csr')
                    y_train = scipy.sparse.vstack((csr_matrix(y_train), csr_matrix(y[span].reshape(-1, 1))),
                                                  format='csr')

            end_span = span[0] + len(span)
            from_span = start_span
            for span in subject_name_by_sequence[inst + 5]:
                next_idx = curr_idx + len(span)
                to_span = from_span + len(span)
                padding_dim = max(self._max_queries - (next_idx - curr_idx), 0)
                if padding_dim == 0:
                    curr_idx = next_idx
                    from_span = to_span
                    continue

                X_seq = X[from_span:to_span].transpose()
                X_seq_padding = csr_matrix(np.zeros((X_seq.shape[0], padding_dim)), dtype='int32')
                X_seq = scipy.sparse.hstack([X_seq_padding, X_seq], format='csr')
                if X_train_seq == []:
                    X_train_seq = X_seq
                else:
                    X_train_seq = scipy.sparse.vstack([X_train_seq, X_seq], format='csr')

                # assign y_seq to the current context labels (e.g., if context has one setup utterance, one request,
                # and one conclusion utterance, then y_seq=[0,1,2])).
                y_seq = y[from_span:to_span]

                # If y_seq=[0,1,2] then that means we need to create 17 more array elements to pad y_seq, so that we
                # reconstruct the 20 element size for a given context. So, y_seq_padding=
                # [3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3].
                # Hence, y_seq_padding holds 17 elements.
                y_seq_padding = np.zeros((padding_dim))
                y_seq_padding += blank_idx

                # Now we concatenate y_seq_padding and y_seq to obtain [3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,0,1,2]
                y_seq = scipy.sparse.vstack([
                    csr_matrix(y_seq_padding.reshape(y_seq_padding.shape + (1,))),
                    csr_matrix(y_seq.reshape(y_seq.shape + (1,)))], format='csr')
                if y_train_seq == []:
                    y_train_seq = y_seq
                else:
                    y_train_seq = scipy.sparse.vstack([y_train_seq, y_seq], format='csr')

                curr_idx = next_idx
                from_span = to_span
                if end_span == (span[0] + len(span)):
                    break

            X_train_seq = X_train_seq[:self._max_sequence_length * \
                                       int(X_train_seq.shape[0] / self._max_sequence_length)]
            X_train_seq_arr = []
            for idx in range(self._max_queries):
                X_train_seq_arr.append(X_train_seq[:, idx].reshape(-1, self._max_sequence_length, 1).toarray())

            y_train_seq_arr = np.asarray(y_train_seq.todense()). \
                reshape(int(y_train_seq.shape[0] / self._max_queries), self._max_queries)

            y_train_seq_arr = y_train_seq_arr.reshape(y_train_seq_arr.shape[0], y_train_seq_arr.shape[1], 1)

            if self._is_sequence_model:
                level_info.set_bottom_level((None, None,
                                             X_train_seq_arr, y_train_seq_arr, None, None, None, setup_idx,
                                             conclusion_idx))
            else:
                level_info.set_bottom_level((None, None,
                                             X_train, y_train.toarray().reshape(y_train.shape[0], ), None, None, None,
                                             setup_idx, conclusion_idx))
        return level_info

    '''
    This method trains the model along a single split of train and test.
    '''

    def _get_single_train_test_split(self):
        data = self._get_data()

        kfold = KFold(n_splits=2, shuffle=True, random_state=7)
        if data.get_top_level():
            total_subjects = len(data.get_top_level()[
                                     0])  # both top and bottom subject name by index will have 16 subjects
                                          # (doesn't matter which one to use here).
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

                X_train_seq = []
                y_train_seq = []
                X_test_seq = []
                y_test_seq = []

                X_train_utt = []
                X_test_utt = []

                y_test_seq_spans = []

                y_cat = np_utils.to_categorical(y)

                # index for 'PAD'
                blank_idx = 0

                curr_idx = 0
                # Note (X,y,X_raw,y_raw) all start with subject 10. On the other hand, depending on where the
                # the k cross fold split happens, this may not line up exactly the same with (X_train,y_train).
                # In other words, they could start with different subject.
                for inst in train:
                    start_span = None
                    for span in subject_name_by_index[inst + 5]:
                        if not start_span:
                            start_span = span[0]
                        for utt in X_utterances[span[0]:(span[0] + len(span))]:
                            X_train_utt.append(utt)
                        if X_train == []:
                            X_train = X[span]
                            y_train = y[span].reshape(-1, 1)
                            continue
                        X_train = scipy.sparse.vstack((X_train, X[span]), format='csr')
                        y_train = scipy.sparse.vstack((csr_matrix(y_train), csr_matrix(y[span].reshape(-1, 1))),
                                                      format='csr')

                    end_span = span[0] + len(span)
                    from_span = start_span
                    for span in subject_name_by_sequence[inst + 5]:
                        next_idx = curr_idx + len(span)
                        to_span = from_span + len(span)
                        padding_dim = max(self._max_queries - (next_idx - curr_idx), 0)
                        if padding_dim == 0:
                            curr_idx = next_idx
                            from_span = to_span
                            continue

                        X_seq = X[from_span:to_span].transpose()
                        X_seq_padding = csr_matrix(np.zeros((X_seq.shape[0], padding_dim)), dtype='int32')
                        X_seq = scipy.sparse.hstack([X_seq_padding, X_seq], format='csr')
                        if X_train_seq == []:
                            X_train_seq = X_seq
                        else:
                            X_train_seq = scipy.sparse.vstack([X_train_seq, X_seq], format='csr')

                        # assign y_seq to the current context labels (e.g., if context has one setup utterance, one
                        # request, and one conclusion utterance, then y_seq=[0,1,2])).
                        y_seq = y[from_span:to_span]

                        # If y_seq=[0,1,2] then that means we need to create 17 more array elements to pad y_seq, so
                        # that we reconstruct the 20 element size for a given context. So, y_seq_padding=
                        # [3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3]. Hence, y_seq_padding holds 17 elements.
                        y_seq_padding = np.zeros((padding_dim))
                        y_seq_padding += blank_idx

                        # Now we concatenate y_seq_padding and y_seq to obtain [3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,0,1,2]
                        y_seq = scipy.sparse.vstack([ \
                            csr_matrix(y_seq_padding.reshape(y_seq_padding.shape + (1,))), \
                            csr_matrix(y_seq.reshape(y_seq.shape + (1,)))], format='csr')
                        if y_train_seq == []:
                            y_train_seq = y_seq
                        else:
                            y_train_seq = scipy.sparse.vstack([y_train_seq, y_seq], format='csr')

                        curr_idx = next_idx
                        from_span = to_span
                        if end_span == (span[0] + len(span)):
                            break

                # Similar notes are applicable in the below code for the test data as they are for the above train data,
                # so skipping comments.
                curr_idx = 0
                start_span = None
                for inst in test:
                    span = subject_name_by_index[inst + 5][0]
                    start_span = span[0]
                    for utt in X_utterances[span[0]:(span[0] + len(span))]:
                        X_test_utt.append(utt)
                    if X_test == []:
                        X_test = X[span]
                        y_test = y[span].reshape(-1, 1)
                    else:
                        X_test = scipy.sparse.vstack((X_test, X[span]), format='csr')
                        y_test = scipy.sparse.vstack((csr_matrix(y_test), csr_matrix(y[span].reshape(-1, 1))),
                                                     format='csr')

                    end_span = span[0] + len(span)
                    from_span = start_span
                    for span in subject_name_by_sequence[inst + 5]:
                        next_idx = curr_idx + len(span)
                        to_span = from_span + len(span)
                        padding_dim = max(self._max_queries - (next_idx - curr_idx), 0)
                        if padding_dim == 0:
                            y_test_seq_spans.append(range(curr_idx, next_idx))
                            curr_idx = next_idx
                            from_span = to_span
                            if end_span == (span[0] + len(span)):
                                break
                            else:
                                continue

                        X_seq = X[from_span:to_span].transpose()
                        X_seq_padding = csr_matrix(np.zeros((X_seq.shape[0], padding_dim)), dtype='int32')
                        X_seq = scipy.sparse.hstack([X_seq_padding, X_seq], format='csr')
                        if X_test_seq == []:
                            X_test_seq = X_seq
                        else:
                            X_test_seq = scipy.sparse.vstack([X_test_seq, X_seq], format='csr')

                        y_seq = y[from_span:to_span]
                        y_seq_padding = np.zeros((padding_dim))
                        y_seq_padding += blank_idx
                        y_seq = scipy.sparse.vstack([csr_matrix(y_seq_padding.reshape(y_seq_padding.shape + (1,))),
                                                     csr_matrix(y_seq.reshape(y_seq.shape + (1,)))], format='csr')
                        if y_test_seq == []:
                            y_test_seq = y_seq
                        else:
                            y_test_seq = scipy.sparse.vstack([y_test_seq, y_seq], format='csr')

                        y_test_seq_spans.append(range(curr_idx, next_idx))
                        curr_idx = next_idx
                        from_span = to_span
                        if end_span == (span[0] + len(span)):
                            break

                X_train_seq = X_train_seq[:self._max_sequence_length * \
                                           int(X_train_seq.shape[0] / self._max_sequence_length)]
                X_train_seq_arr = []
                for idx_seq in range(self._max_queries):
                    X_train_seq_arr.append(X_train_seq[:, idx_seq]. \
                                           reshape(-1, self._max_sequence_length, 1).toarray())

                X_test_seq = X_test_seq[:self._max_sequence_length * \
                                         int(X_test_seq.shape[0] / self._max_sequence_length)]
                X_test_seq_arr = []
                for idx_seq in range(self._max_queries):
                    X_test_seq_arr.append(X_test_seq[:, idx_seq]. \
                                          reshape(-1, self._max_sequence_length, 1).toarray())

                y_train_seq_arr = np.asarray(y_train_seq.todense()). \
                    reshape(int(y_train_seq.shape[0] / self._max_queries), self._max_queries)
                y_test_seq_arr = np.asarray(y_test_seq.todense()). \
                    reshape(int(y_test_seq.shape[0] / self._max_queries), self._max_queries)

                y_train_seq_arr = y_train_seq_arr.reshape(y_train_seq_arr.shape[0], y_train_seq_arr.shape[1], 1)
                y_test_seq_arr = y_test_seq_arr.reshape(y_test_seq_arr.shape[0], y_test_seq_arr.shape[1], 1)

                if self._is_sequence_model:
                    level_info.set_top_level((train, test,
                                              X_train_seq_arr, y_train_seq_arr, X_test_seq_arr, y_test_seq_arr,
                                              y_test_seq_spans, setup_idx, conclusion_idx))
                else:
                    level_info.set_top_level((train, test,
                                              X_train, y_train.toarray().reshape(y_train.shape[0], ), X_test,
                                              y_test.toarray().reshape(y_test.shape[0], ),
                                              y_test_seq_spans, setup_idx, conclusion_idx))

            if data.get_bottom_level():
                subject_name_by_index, subject_name_by_sequence, X_raw, y_raw, y_raw_sequence, CLASSES, X_utterances, \
                X, y = data.get_bottom_level()

                setup_idx, conclusion_idx = -1, -1

                X_train = []
                y_train = []
                X_test = []
                y_test = []

                X_train_seq = []
                y_train_seq = []
                X_test_seq = []
                y_test_seq = []

                X_train_utt = []
                X_test_utt = []

                y_test_seq_spans = []

                y_cat = np_utils.to_categorical(y)

                # index for 'PAD'
                blank_idx = 0

                curr_idx = 0
                # Note (X,y,X_raw,y_raw) all start with subject 10. On the other hand, depending on where the
                # the k cross fold split happens, this may not line up exactly the same with (X_train,y_train).
                # In other words, they could start with different subject.
                for inst in train:
                    start_span = None
                    for span in subject_name_by_index[inst + 5]:
                        if not start_span:
                            start_span = span[0]
                        for utt in X_utterances[span[0]:(span[0] + len(span))]:
                            X_train_utt.append(utt)
                        if X_train == []:
                            X_train = X[span]
                            y_train = y[span].reshape(-1, 1)
                            continue
                        X_train = scipy.sparse.vstack((X_train, X[span]), format='csr')
                        y_train = scipy.sparse.vstack((csr_matrix(y_train), csr_matrix(y[span].reshape(-1, 1))),
                                                      format='csr')

                    end_span = span[0] + len(span)
                    from_span = start_span
                    for span in subject_name_by_sequence[inst + 5]:
                        next_idx = curr_idx + len(span)
                        to_span = from_span + len(span)
                        padding_dim = max(self._max_queries - (next_idx - curr_idx), 0)
                        if padding_dim == 0:
                            curr_idx = next_idx
                            from_span = to_span
                            continue

                        X_seq = X[from_span:to_span].transpose()
                        X_seq_padding = csr_matrix(np.zeros((X_seq.shape[0], padding_dim)), dtype='int32')
                        X_seq = scipy.sparse.hstack([X_seq_padding, X_seq], format='csr')
                        if X_train_seq == []:
                            X_train_seq = X_seq
                        else:
                            X_train_seq = scipy.sparse.vstack([X_train_seq, X_seq], format='csr')

                        # assign y_seq to the current context labels (e.g., if context has one setup utterance, one
                        # request, and one conclusion utterance, then y_seq=[0,1,2])).
                        y_seq = y[from_span:to_span]

                        # If y_seq=[0,1,2] then that means we need to create 17 more array elements to pad y_seq,
                        # so that we reconstruct the 20 element size for a given context. So, y_seq_padding=
                        # [3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3]. Hence, y_seq_padding holds 17 elements.
                        y_seq_padding = np.zeros((padding_dim))
                        y_seq_padding += blank_idx

                        # Now we concatenate y_seq_padding and y_seq to obtain [3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,0,1,2]
                        y_seq = scipy.sparse.vstack([
                            csr_matrix(y_seq_padding.reshape(y_seq_padding.shape + (1,))),
                            csr_matrix(y_seq.reshape(y_seq.shape + (1,)))], format='csr')
                        if y_train_seq == []:
                            y_train_seq = y_seq
                        else:
                            y_train_seq = scipy.sparse.vstack([y_train_seq, y_seq], format='csr')

                        curr_idx = next_idx
                        from_span = to_span
                        if end_span == (span[0] + len(span)):
                            break

                # Similar notes are applicable in the below code for the test data as they are for the above train data,
                # so skipping comments.
                curr_idx = 0
                start_span = None
                for inst in test:
                    span = subject_name_by_index[inst + 5][0]
                    start_span = span[0]
                    for utt in X_utterances[span[0]:(span[0] + len(span))]:
                        X_test_utt.append(utt)
                    if X_test == []:
                        X_test = X[span]
                        y_test = y[span].reshape(-1, 1)
                    else:
                        X_test = scipy.sparse.vstack((X_test, X[span]), format='csr')
                        y_test = scipy.sparse.vstack((csr_matrix(y_test), csr_matrix(y[span].reshape(-1, 1))),
                                                     format='csr')

                    end_span = span[0] + len(span)
                    from_span = start_span
                    for span in subject_name_by_sequence[inst + 5]:
                        next_idx = curr_idx + len(span)
                        to_span = from_span + len(span)
                        padding_dim = max(self._max_queries - (next_idx - curr_idx), 0)
                        if padding_dim == 0:
                            y_test_seq_spans.append(range(curr_idx, next_idx))
                            curr_idx = next_idx
                            from_span = to_span
                            if end_span == (span[0] + len(span)):
                                break
                            else:
                                continue

                        X_seq = X[from_span:to_span].transpose()
                        X_seq_padding = csr_matrix(np.zeros((X_seq.shape[0], padding_dim)), dtype='int32')
                        X_seq = scipy.sparse.hstack([X_seq_padding, X_seq], format='csr')
                        if X_test_seq == []:
                            X_test_seq = X_seq
                        else:
                            X_test_seq = scipy.sparse.vstack([X_test_seq, X_seq], format='csr')

                        y_seq = y[from_span:to_span]
                        y_seq_padding = np.zeros((padding_dim))
                        y_seq_padding += blank_idx
                        y_seq = scipy.sparse.vstack([csr_matrix(y_seq_padding.reshape(y_seq_padding.shape + (1,))),
                                                     csr_matrix(y_seq.reshape(y_seq.shape + (1,)))], format='csr')
                        if y_test_seq == []:
                            y_test_seq = y_seq
                        else:
                            y_test_seq = scipy.sparse.vstack([y_test_seq, y_seq], format='csr')

                        y_test_seq_spans.append(range(curr_idx, next_idx))
                        curr_idx = next_idx
                        from_span = to_span
                        if end_span == (span[0] + len(span)):
                            break

                X_train_seq = X_train_seq[:self._max_sequence_length * \
                                           int(X_train_seq.shape[0] / self._max_sequence_length)]
                X_train_seq_arr = []
                for idx_seq in range(self._max_queries):
                    X_train_seq_arr.append(X_train_seq[:, idx_seq]. \
                                           reshape(-1, self._max_sequence_length, 1).toarray())

                X_test_seq = X_test_seq[:self._max_sequence_length * \
                                         int(X_test_seq.shape[0] / self._max_sequence_length)]
                X_test_seq_arr = []
                for idx_seq in range(self._max_queries):
                    X_test_seq_arr.append(X_test_seq[:, idx_seq]. \
                                          reshape(-1, self._max_sequence_length, 1).toarray())

                y_train_seq_arr = np.asarray(y_train_seq.todense()). \
                    reshape(int(y_train_seq.shape[0] / self._max_queries), self._max_queries)
                y_test_seq_arr = np.asarray(y_test_seq.todense()). \
                    reshape(int(y_test_seq.shape[0] / self._max_queries), self._max_queries)

                y_train_seq_arr = y_train_seq_arr.reshape(y_train_seq_arr.shape[0], y_train_seq_arr.shape[1], 1)
                y_test_seq_arr = y_test_seq_arr.reshape(y_test_seq_arr.shape[0], y_test_seq_arr.shape[1], 1)

                if self._is_sequence_model:
                    level_info.set_bottom_level((train, test,
                                                 X_train_seq_arr, y_train_seq_arr, X_test_seq_arr, y_test_seq_arr,
                                                 y_test_seq_spans, setup_idx, conclusion_idx))
                else:
                    level_info.set_bottom_level((train, test,
                                                 X_train, y_train.toarray().reshape(y_train.shape[0], ), X_test,
                                                 y_test.toarray().reshape(y_test.shape[0], ),
                                                 y_test_seq_spans, -1, -1))
            kfolddata.append(level_info)

            # just go through one itereation of the loop
            return kfolddata

    '''
    This method is nearly identical to _get_single_train_test_split with the caveat that its not just a single split 
    since here we are doing full-fledged cross validation.
    '''

    def _get_cross_validation_train_test_split(self):
        data = self._get_data()

        kfold = KFold(n_splits=self._k_cross_validation, shuffle=True, random_state=7)
        if data.get_top_level():
            total_subjects = len(data.get_top_level()[
                                     0])  # both top and bottom subject name by index will have 16 subjects
                                          # (doesn't matter which one to use here).
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
                print("TRAIN", train, "TEST", test)
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

                X_train_seq = []
                y_train_seq = []
                X_test_seq = []
                y_test_seq = []

                X_train_utt = []
                X_test_utt = []

                y_test_seq_spans = []

                y_cat = np_utils.to_categorical(y)

                # index for 'PAD'
                blank_idx = 0

                curr_idx = 0
                # Note (X,y,X_raw,y_raw) all start with subject 10. On the other hand, depending on where the
                # the k cross fold split happens, this may not line up exactly the same with (X_train,y_train).
                # In other words, they could start with different subject.
                for inst in train:
                    start_span = None
                    for span in subject_name_by_index[inst + 5]:
                        if not start_span:
                            start_span = span[0]
                        for utt in X_utterances[span[0]:(span[0] + len(span))]:
                            X_train_utt.append(utt)
                        if X_train == []:
                            X_train = X[span]
                            y_train = y[span].reshape(-1, 1)
                            continue
                        X_train = scipy.sparse.vstack((X_train, X[span]), format='csr')
                        y_train = scipy.sparse.vstack((csr_matrix(y_train), csr_matrix(y[span].reshape(-1, 1))),
                                                      format='csr')

                    end_span = span[0] + len(span)
                    from_span = start_span
                    for span in subject_name_by_sequence[inst + 5]:
                        next_idx = curr_idx + len(span)
                        to_span = from_span + len(span)
                        padding_dim = max(self._max_queries - (next_idx - curr_idx), 0)
                        if padding_dim == 0:
                            curr_idx = next_idx
                            from_span = to_span
                            continue
                        X_seq = X[from_span:to_span].transpose()
                        X_seq_padding = csr_matrix(np.zeros((X_seq.shape[0], padding_dim)), dtype='int32')
                        X_seq = scipy.sparse.hstack([X_seq_padding, X_seq], format='csr')
                        if X_train_seq == []:
                            X_train_seq = X_seq
                        else:
                            X_train_seq = scipy.sparse.vstack([X_train_seq, X_seq], format='csr')

                        # assign y_seq to the current context labels (e.g., if context has one setup utterance, one
                        # request, and one conclusion utterance, then y_seq=[0,1,2])).
                        y_seq = y[from_span:to_span]

                        # If y_seq=[0,1,2] then that means we need to create 17 more array elements to pad y_seq, so
                        # that we reconstruct the 20 element size for a given context. So, y_seq_padding=
                        # [3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3]. Hence, y_seq_padding holds 17 elements.
                        y_seq_padding = np.zeros((padding_dim))
                        y_seq_padding += blank_idx

                        # Now we concatenate y_seq_padding and y_seq to obtain [3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,0,1,2]
                        y_seq = scipy.sparse.vstack([
                            csr_matrix(y_seq_padding.reshape(y_seq_padding.shape + (1,))),
                            csr_matrix(y_seq.reshape(y_seq.shape + (1,)))], format='csr')
                        if y_train_seq == []:
                            y_train_seq = y_seq
                        else:
                            y_train_seq = scipy.sparse.vstack([y_train_seq, y_seq], format='csr')

                        curr_idx = next_idx
                        from_span = to_span
                        if end_span == (span[0] + len(span)):
                            break

                # Similar notes are applicable in the below code for the test data as they are for the above train data,
                # so skipping comments.
                curr_idx = 0
                start_span = None
                for inst in test:
                    span = subject_name_by_index[inst + 5][0]
                    start_span = span[0]
                    for utt in X_utterances[span[0]:(span[0] + len(span))]:
                        X_test_utt.append(utt)
                    if X_test == []:
                        X_test = X[span]
                        y_test = y[span].reshape(-1, 1)
                    else:
                        X_test = scipy.sparse.vstack((X_test, X[span]), format='csr')
                        y_test = scipy.sparse.vstack((csr_matrix(y_test), csr_matrix(y[span].reshape(-1, 1))),
                                                     format='csr')
                    end_span = span[0] + len(span)
                    from_span = start_span
                    for span in subject_name_by_sequence[inst + 5]:
                        next_idx = curr_idx + len(span)
                        to_span = from_span + len(span)
                        padding_dim = max(self._max_queries - (next_idx - curr_idx), 0)
                        if padding_dim == 0:
                            y_test_seq_spans.append(range(curr_idx, next_idx))
                            curr_idx = next_idx
                            from_span = to_span
                            if end_span == (span[0] + len(span)):
                                break
                            else:
                                continue
                        X_seq = X[from_span:to_span].transpose()
                        X_seq_padding = csr_matrix(np.zeros((X_seq.shape[0], padding_dim)), dtype='int32')
                        X_seq = scipy.sparse.hstack([X_seq_padding, X_seq], format='csr')
                        if X_test_seq == []:
                            X_test_seq = X_seq
                        else:
                            X_test_seq = scipy.sparse.vstack([X_test_seq, X_seq], format='csr')

                        y_seq = y[from_span:to_span]
                        y_seq_padding = np.zeros((padding_dim))
                        y_seq_padding += blank_idx
                        y_seq = scipy.sparse.vstack([csr_matrix(y_seq_padding.reshape(y_seq_padding.shape + (1,))),
                                                     csr_matrix(y_seq.reshape(y_seq.shape + (1,)))], format='csr')
                        if y_test_seq == []:
                            y_test_seq = y_seq
                        else:
                            y_test_seq = scipy.sparse.vstack([y_test_seq, y_seq], format='csr')

                        y_test_seq_spans.append(range(curr_idx, next_idx))
                        curr_idx = next_idx
                        from_span = to_span
                        if end_span == (span[0] + len(span)):
                            break

                X_train_seq = X_train_seq[:self._max_sequence_length * \
                                           int(X_train_seq.shape[0] / self._max_sequence_length)]
                X_train_seq_arr = []
                for idx_seq in range(self._max_queries):
                    X_train_seq_arr.append(X_train_seq[:, idx_seq]. \
                                           reshape(-1, self._max_sequence_length).toarray())

                X_test_seq = X_test_seq[:self._max_sequence_length * \
                                         int(X_test_seq.shape[0] / self._max_sequence_length)]
                X_test_seq_arr = []
                for idx_seq in range(self._max_queries):
                    X_test_seq_arr.append(X_test_seq[:, idx_seq]. \
                                          reshape(-1, self._max_sequence_length).toarray())

                y_train_seq_arr = np.asarray(y_train_seq.todense()). \
                    reshape(int(y_train_seq.shape[0] / self._max_queries), self._max_queries)
                y_test_seq_arr = np.asarray(y_test_seq.todense()). \
                    reshape(int(y_test_seq.shape[0] / self._max_queries), self._max_queries)

                y_train_seq_arr = y_train_seq_arr.reshape(y_train_seq_arr.shape[0], y_train_seq_arr.shape[1], 1)
                y_test_seq_arr = y_test_seq_arr.reshape(y_test_seq_arr.shape[0], y_test_seq_arr.shape[1], 1)

                if self._is_sequence_model:
                    level_info.set_top_level((train, test,
                                              X_train_seq_arr, y_train_seq_arr, X_test_seq_arr, y_test_seq_arr,
                                              y_test_seq_spans, setup_idx, conclusion_idx))
                else:
                    level_info.set_top_level((train, test,
                                              X_train, y_train.toarray().reshape(y_train.shape[0], ), X_test,
                                              y_test.toarray().reshape(y_test.shape[0], ),
                                              y_test_seq_spans, setup_idx, conclusion_idx))

            if data.get_bottom_level():
                subject_name_by_index, subject_name_by_sequence, X_raw, y_raw, y_raw_sequence, CLASSES, X_utterances, \
                X, y = data.get_bottom_level()

                X_train = []
                y_train = []
                X_test = []
                y_test = []

                X_train_seq = []
                y_train_seq = []
                X_test_seq = []
                y_test_seq = []

                X_train_utt = []
                X_test_utt = []

                y_test_seq_spans = []

                y_cat = np_utils.to_categorical(y)

                # index for 'PAD'
                blank_idx = 0

                curr_idx = 0
                # Note (X,y,X_raw,y_raw) all start with subject 10. On the other hand, depending on where the
                # the k cross fold split happens, this may not line up exactly the same with (X_train,y_train).
                # In other words, they could start with different subject.
                for inst in train:
                    start_span = None
                    for span in subject_name_by_index[inst + 5]:
                        if not start_span:
                            start_span = span[0]
                        for utt in X_utterances[span[0]:(span[0] + len(span))]:
                            X_train_utt.append(utt)
                        if X_train == []:
                            X_train = X[span]
                            y_train = y[span].reshape(-1, 1)
                            continue
                        X_train = scipy.sparse.vstack((X_train, X[span]), format='csr')
                        y_train = scipy.sparse.vstack((csr_matrix(y_train), csr_matrix(y[span].reshape(-1, 1))),
                                                      format='csr')

                    end_span = span[0] + len(span)
                    from_span = start_span
                    for span in subject_name_by_sequence[inst + 5]:
                        next_idx = curr_idx + len(span)
                        to_span = from_span + len(span)
                        padding_dim = max(self._max_queries - (next_idx - curr_idx), 0)
                        if padding_dim == 0:
                            curr_idx = next_idx
                            from_span = to_span
                            continue

                        X_seq = X[from_span:to_span].transpose()
                        X_seq_padding = csr_matrix(np.zeros((X_seq.shape[0], padding_dim)), dtype='int32')
                        X_seq = scipy.sparse.hstack([X_seq_padding, X_seq], format='csr')
                        if X_train_seq == []:
                            X_train_seq = X_seq
                        else:
                            X_train_seq = scipy.sparse.vstack([X_train_seq, X_seq], format='csr')

                        # assign y_seq to the current context labels (e.g., if context has one setup utterance, one
                        # request, and one conclusion utterance, then y_seq=[0,1,2])).
                        y_seq = y[from_span:to_span]

                        # If y_seq=[0,1,2] then that means we need to create 17 more array elements to pad y_seq, so
                        # that we reconstruct the 20 element size for a given context. So, y_seq_padding=
                        # [3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3].
                        # Hence, y_seq_padding holds 17 elements.
                        y_seq_padding = np.zeros((padding_dim))
                        y_seq_padding += blank_idx

                        # Now we concatenate y_seq_padding and y_seq to obtain [3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,0,1,2]
                        y_seq = scipy.sparse.vstack([
                            csr_matrix(y_seq_padding.reshape(y_seq_padding.shape + (1,))),
                            csr_matrix(y_seq.reshape(y_seq.shape + (1,)))], format='csr')
                        if y_train_seq == []:
                            y_train_seq = y_seq
                        else:
                            y_train_seq = scipy.sparse.vstack([y_train_seq, y_seq], format='csr')

                        curr_idx = next_idx
                        from_span = to_span
                        if end_span == (span[0] + len(span)):
                            break

                # Similar notes are applicable in the below code for the test data as they are for the above train data,
                # so skipping comments.
                curr_idx = 0
                start_span = None
                for inst in test:
                    span = subject_name_by_index[inst + 5][0]
                    start_span = span[0]
                    for utt in X_utterances[span[0]:(span[0] + len(span))]:
                        X_test_utt.append(utt)
                    if X_test == []:
                        X_test = X[span]
                        y_test = y[span].reshape(-1, 1)
                    else:
                        X_test = scipy.sparse.vstack((X_test, X[span]), format='csr')
                        y_test = scipy.sparse.vstack((csr_matrix(y_test), csr_matrix(y[span].reshape(-1, 1))),
                                                     format='csr')

                    end_span = span[0] + len(span)
                    from_span = start_span
                    for span in subject_name_by_sequence[inst + 5]:
                        next_idx = curr_idx + len(span)
                        to_span = from_span + len(span)
                        padding_dim = max(self._max_queries - (next_idx - curr_idx), 0)
                        if padding_dim == 0:
                            y_test_seq_spans.append(range(curr_idx, next_idx))
                            curr_idx = next_idx
                            from_span = to_span
                            if end_span == (span[0] + len(span)):
                                break
                            else:
                                continue

                        X_seq = X[from_span:to_span].transpose()
                        X_seq_padding = csr_matrix(np.zeros((X_seq.shape[0], padding_dim)), dtype='int32')
                        X_seq = scipy.sparse.hstack([X_seq_padding, X_seq], format='csr')
                        if X_test_seq == []:
                            X_test_seq = X_seq
                        else:
                            X_test_seq = scipy.sparse.vstack([X_test_seq, X_seq], format='csr')

                        y_seq = y[from_span:to_span]
                        y_seq_padding = np.zeros((padding_dim))
                        y_seq_padding += blank_idx
                        y_seq = scipy.sparse.vstack([csr_matrix(y_seq_padding.reshape(y_seq_padding.shape + (1,))),
                                                     csr_matrix(y_seq.reshape(y_seq.shape + (1,)))], format='csr')
                        if y_test_seq == []:
                            y_test_seq = y_seq
                        else:
                            y_test_seq = scipy.sparse.vstack([y_test_seq, y_seq], format='csr')

                        y_test_seq_spans.append(range(curr_idx, next_idx))
                        curr_idx = next_idx
                        from_span = to_span
                        if end_span == (span[0] + len(span)):
                            break
                X_train_seq = X_train_seq[:self._max_sequence_length * \
                                           int(X_train_seq.shape[0] / self._max_sequence_length)]
                X_train_seq_arr = []
                for idx_seq in range(self._max_queries):
                    X_train_seq_arr.append(X_train_seq[:, idx_seq]. \
                                           reshape(-1, self._max_sequence_length).toarray())

                X_test_seq = X_test_seq[:self._max_sequence_length * \
                                         int(X_test_seq.shape[0] / self._max_sequence_length)]
                X_test_seq_arr = []
                for idx_seq in range(self._max_queries):
                    X_test_seq_arr.append(X_test_seq[:, idx_seq]. \
                                          reshape(-1, self._max_sequence_length).toarray())

                y_train_seq_arr = np.asarray(y_train_seq.todense()). \
                    reshape(int(y_train_seq.shape[0] / self._max_queries), self._max_queries)
                y_test_seq_arr = np.asarray(y_test_seq.todense()). \
                    reshape(int(y_test_seq.shape[0] / self._max_queries), self._max_queries)

                y_train_seq_arr = y_train_seq_arr.reshape(y_train_seq_arr.shape[0], y_train_seq_arr.shape[1], 1)
                y_test_seq_arr = y_test_seq_arr.reshape(y_test_seq_arr.shape[0], y_test_seq_arr.shape[1], 1)

                if self._is_sequence_model:
                    level_info.set_bottom_level((train, test,
                                                 X_train_seq_arr, y_train_seq_arr, X_test_seq_arr, y_test_seq_arr,
                                                 y_test_seq_spans, -1, -1))
                else:
                    level_info.set_bottom_level((train, test,
                                                 X_train, y_train.toarray().reshape(y_train.shape[0], ), X_test,
                                                 y_test.toarray().reshape(y_test.shape[0], ),
                                                 y_test_seq_spans, -1, -1))
            kfolddata.append(level_info)

        return kfolddata

    '''
    The _get_data() method retrieves all the appropriate data needed for training.

    N (the total subjects) = TOTAL_VERSIONS * 16 subjects (e.g., 160 subjects when 10 versions are generated by 
    paraphraser). C (the total contexts) = 4400 when TOTAL_VERSIONS=10. And also suppose N=15.3K utterances.


    X: is the index representation of all N utterances produced by paraphraser.
    Dimenions are N X Z. In our example, this is (15.3K, 216.K) dimentions if the largest feature vector is 216.6K in 
    size. Note that tfidf.fit_transform(X_raw) would create X.\

    X_raw[0] is semicolon separated features for the first utterance. len(X_raw) is N. In our example this is 15.3K.

    y: is the index representation of all N labels, one for each utterance produced by paraphraser.
    Dimensions are N X 1. In our example, this is (15.3K, 1) dimensions. Note that labelencoder.fit_transform(y_raw) 
    produce y.

    y_raw[0] is the label for the first utterance. len(y_raw) is N. In our example this is 15.3K.

    X_utterances: the actual N utterances produced. In our example, len(X_utternces) is 15.3K in size.

    subject_name_by_index: For each of the 16 subjects (subject 5 through subject 20), there are TOTAL_VERSIONS 
    associated ranges. Each range represents the start through end indices for each of the TOTAL_VERSIONS versions 
    generated by the paraphraser. (e.g., subject_name_by_index[5] contains 10 elements, each element is a range 
    representing 1 of the 10 total versions generated by the paraphraser, when TOTAL_VERSIONS=10). In all, total 
    elements is therefore 16 subjects * TOTAL_VERSIONS = 160. Clearly, if you sum up all the range lengths, that will 
    equal the total utterances N.

    subject_name_by_sequence: For each of the 16 subjects (subject 5 through subject 20), there are range elements for 
    each annotated context. X_utterances[subject_name_by_sequence][5][0] for example produces the first context for 
    subject 5. When TOTAL_VERSIONS=10, ther are approximately C=4400 total contexts and clearly if you sum up all the 
    range elements in this dictionary, it will be N.
    '''

    def _get_data(self):
        level_info = Level()

        if self._classification_level == ClassificationLevelConfig.TOP_LEVEL or self._classification_level == ClassificationLevelConfig.TWO_LEVEL:
            print("Extracting top level data...")
            feature_builder = SequenceFeatureVectors(feature_extractor=self._feature_extractor.get_top_level())
            subject_name_by_index, subject_name_by_sequence, X_raw, y_raw, y_raw_sequence, embedding_weights, \
            index_to_word, word_to_index, vocab_size, CLASSES, X_utterances, X, y, tokenizer, tag2idx, idx2tag = \
                feature_builder.extract(
                    corpus_path=self._corpus_path,
                    tokenize=self._use_tokenizer,
                    include_setup=True,
                    include_request=True,
                    include_conclusion=True,
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
                    include_number_of_non_modal_verbs=False,
                    include_number_of_wh_words=False,
                    max_sequence_length=self._max_sequence_length,
                    IGNORE_CLASSES=['appearance', 'big high level question'],
                    MERGE_CLASSES=['createvis', 'modifyvis', 'factbased', 'preference', 'winmgmt', 'clarification'],
                    is_corpus_json=self._use_paraphrasing,
                    total_versions=self._total_versions)

            self._tokenizer.set_top_level(tokenizer)

            if self._is_sequence_model:
                tag2idx = {tag:idx+1 for tag,idx in tag2idx.items()}
                tag2idx['PAD'] = 0
                idx2tag = {idx:tag for tag,idx in tag2idx.items()}
                y += 1
            self._tag2idx.set_top_level(tag2idx)
            self._idx2tag.set_top_level(idx2tag)
            self._embedding_weights.set_top_level(embedding_weights)
            self._vocab_size.set_top_level(vocab_size)
            self._classes.set_top_level(CLASSES)
            level_info.set_top_level((subject_name_by_index, subject_name_by_sequence, X_raw, y_raw, y_raw_sequence,
                                      CLASSES, X_utterances, X, y))

        if self._classification_level == ClassificationLevelConfig.BOTTOM_LEVEL or self._classification_level == ClassificationLevelConfig.TWO_LEVEL:
            print("Extracting bottom level data...")
            feature_builder = SequenceFeatureVectors(feature_extractor=self._feature_extractor.get_bottom_level())
            subject_name_by_index, subject_name_by_sequence, X_raw, y_raw, y_raw_sequence, embedding_weights, \
            index_to_word, word_to_index, vocab_size, CLASSES, X_utterances, X, y, tokenizer, tag2idx, idx2tag = \
                feature_builder.extract(
                    corpus_path=self._corpus_path,
                    tokenize=self._use_tokenizer,
                    include_setup=True,
                    include_request=True,
                    include_conclusion=True,
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
                    include_number_of_non_modal_verbs=False,
                    include_number_of_wh_words=False,
                    max_sequence_length=self._max_sequence_length,
                    IGNORE_CLASSES=['appearance', 'big high level question'],
                    MERGE_CLASSES=['createvis', 'modifyvis'],
                    is_corpus_json=self._use_paraphrasing,
                    total_versions=self._total_versions)

            self._tokenizer.set_bottom_level(tokenizer)
            if self._is_sequence_model:
                tag2idx = {tag:idx+1 for tag,idx in tag2idx.items()}
                tag2idx['PAD'] = 0
                idx2tag = {idx:tag for tag,idx in tag2idx.items()}
                y += 1
            self._tag2idx.set_bottom_level(tag2idx)
            self._idx2tag.set_bottom_level(idx2tag)
            self._embedding_weights.set_bottom_level(embedding_weights)
            self._vocab_size.set_bottom_level(vocab_size)
            self._classes.set_bottom_level(CLASSES)
            level_info.set_bottom_level((subject_name_by_index, subject_name_by_sequence, X_raw, y_raw, y_raw_sequence,
                                         CLASSES, X_utterances, X, y))

        return level_info

    @abstractmethod
    def get_model_architecture(self, words, tags, which_level):
        pass
