import itertools
import random
from os import path

import numpy as np
import pandas as pd
import spacy
from sklearn.model_selection import KFold
from spacy.gold import GoldParse
from spacy.scorer import Scorer
from spacy.util import minibatch, compounding

from .referring_expression_extraction_model import ReferringExpressionExtractionModel
from .useembeddingconfig import UseEmbeddingConfig


class SPACYModel(ReferringExpressionExtractionModel):
    def __init__(self):
        super().__init__(name='SPACYModel')

    def train(self, \
              ner_csv_files, \
              k_cross_validation=5, \
              iterations=10, \
              embedding_type=UseEmbeddingConfig.USE_CRIME_EMBEDDING, \
              overwrite=False, \
              max_sequence_length=None, \
              evaluate=False, \
              embedding_dim=100):

        super().train( \
            ner_csv_files, \
            k_cross_validation, \
            iterations, \
            embedding_type, \
            overwrite, \
            max_sequence_length, \
            evaluate, \
            embedding_dim)

        dropout = 0.2
        display_freq = 1
        performance = 0
        fold = 0
        for X_train, y_train, X_test, y_test in self._get_training_data_fn():
            nlp = spacy.blank('en')

            if 'ner' not in nlp.pipe_names:
                ner = nlp.create_pipe('ner')
                nlp.add_pipe(ner)
            for i in self._tag2idx.keys():
                ner.add_label(str(i)[2:])

            # Disable other pipelines in SpaCy to only train NER
            other_pipes = [pipe for pipe in nlp.pipe_names if pipe != 'ner']
            with nlp.disable_pipes(*other_pipes):
                nlp.vocab.vectors.name = 'spacy_model'  # without this, spaCy throws an "unnamed" error
                optimizer = nlp.begin_training(device=0)
                for itr in range(self._iterations):
                    random.shuffle(X_train)  # shuffle the training data before each iteration
                    losses = {}
                    batches = minibatch(X_train, size=compounding(4., 32., 1.001))
                    for batch in batches:
                        texts, annotations = zip(*batch)
                        nlp.update( \
                            texts, \
                            annotations, \
                            drop=dropout, \
                            sgd=optimizer, \
                            losses=losses)
                    if itr % display_freq == 0:
                        print("Iteration {} Loss: {}".format(itr + 1, losses))

            # if we want to evaluate for current fold the following accoplishes this.
            if evaluate:
                print("Evaluating fold", fold, "for model", self._name)
                performance = self._compute_performance(trained_model=nlp, data=X_test, performance_dict=performance)

            fold += 1
            # Now that we trained this model we can yield it for the current fold
            yield nlp

        if evaluate:
            self._print_performance(fold=fold, performance_dict=performance, name=self._name)

    def predict(self, trained_model, utterance):
        pass

    def _get_train_no_split(self):
        # no split so just flatten all the data and return.
        X_per_subject, y_per_subject = self._get_data()
        X = np.asarray(list(itertools.chain(*X_per_subject)))
        y = np.asarray(list(itertools.chain(*y_per_subject)))
        return [X, y, None, None]

    def _get_single_train_test_split(self):
        # Must split across subject verticals not within subjects. Just need a single split.
        # but n_splits=1 is not allowed so we do the trick of n_splits=2 but return from for-loop after just one iteration.
        X_per_subject, y_per_subject = self._get_data()
        k_fold = KFold(n_splits=2, shuffle=True, random_state=7)

        # X_train,y_train,X_test,y_test=[],[],[],[]

        X_p, y_p = np.zeros((self._total_subjects,)), \
                   np.zeros((self._total_subjects,))

        # indices are split for the 16 subjects, into the two lists, train and test.
        for train, test in kfold.split(X_p, y_p):
            X_train, y_train = X_per_subject[train], y_per_subject[train]
            X_train = np.asarray(list(itertools.chain(*X_train)))
            y_train = np.asarray(list(itertools.chain(*y_train)))

            X_test, y_test = X_per_subject[test], y_per_subject[test]
            X_test = np.asarray(list(itertools.chain(*X_test)))
            y_test = np.asarray(list(itertools.chain(*y_test)))

            # just a single iteration is all we need.
            return [X_train, y_train, X_test, y_test]

    def _get_cross_validation_train_test_split(self):
        # Must split across subject verticals not within subjects. We need self._k_cross_validation total folds in our cross validation.
        X_per_subject, y_per_subject = self._get_data()
        k_fold = KFold(n_splits=self._k_cross_validation, shuffle=True, random_state=7)

        X_p, y_p = np.zeros((self._total_subjects,)), \
                   np.zeros((self._total_subjects,))

        # indices are split for the 16 subjects, into the two lists, train and test.
        for train, test in k_fold.split(X_p, y_p):
            X_train, y_train = X_per_subject[train], y_per_subject[train]
            X_train = np.asarray(list(itertools.chain(*X_train)))
            y_train = np.asarray(list(itertools.chain(*y_train)))

            X_test, y_test = X_per_subject[test], y_per_subject[test]
            X_test = np.asarray(list(itertools.chain(*X_test)))
            y_test = np.asarray(list(itertools.chain(*y_test)))

            # For each fold, we yield our training data. Much better to do this then to store the data in array which takes up RAM!
            yield X_train, y_train, X_test, y_test

    def _transform_to_format(self, sentences_pos_tags):
        ''' Converts data from:
        label \t word \n label \t word \n \n label \t word
        to: sentence, {entities : [(start, end, label), (stard, end, label)]}
        '''
        spacy_formatted_data, entities, sentence_data, unique_labels = [], [], [], []
        current_annotation = None
        end = 0  # initialize counter to keep track of start and end characters
        for words_pos_tags in sentences_pos_tags:
            for idx in range(len(words_pos_tags)):
                word = words_pos_tags[idx][0]
                # tags[0]='B-PER' for first sentence, and tags[0][0]='B' and tags[0][2:]='PER'
                tag_type = words_pos_tags[idx][2][0]
                tag = words_pos_tags[idx][2][2:]

                sentence_data.append(word)

                end += (len(word) + 1)  # length of the word + trailing space

                if tag_type != 'I' and current_annotation:  # if at the end of an annotation
                    entities.append((start, end - 2 - len(word), current_annotation))  # append the annotation
                    current_annotation = None  # reset the annotation
                if tag_type == 'B':  # if beginning new annotation
                    start = end - len(word) - 1  # start annotation at beginning of word
                    current_annotation = tag  # append the word to the current annotation
                if tag_type == 'I':  # if the annotation is multi-word
                    current_annotation = tag  # append the word

                if tag != 'O' and tag not in unique_labels:
                    unique_labels.append(tag)

            if current_annotation:
                entities.append((start, end - 1, current_annotation))
            sentence_data = " ".join(sentence_data)
            spacy_formatted_data.append([sentence_data, {'entities': entities}])
            # reset the counters and temporary list.
            end = 0
            entities, sentence_data = [], []
            current_annotation = None
        return spacy_formatted_data, unique_labels

    def _get_data(self):
        # There should be 16 total subjects appended here
        # If we wanted to concatenate the datasets just uncomment line below after the appending line in for-loop below.
        # In our case we cannot do that.
        # dataset=pd.concat(ner_datasets, ignore_index=True)
        pad_token = 'PAD'
        unk_token = 'UNK'
        ner_datasets = []
        for ner_csv_file in self._ner_csv_files:
            ner_dataset = pd.read_csv(ner_csv_file, sep=',', encoding='latin1').fillna(method='ffill')
            ner_datasets.append(ner_dataset)
        all_datasets = pd.concat(ner_datasets, ignore_index=True)

        words = list(set(all_datasets["Word"].values))
        self._n_words = len(words)
        self._word2idx = {w: i + 2 for i, w in enumerate(words)}
        self._word2idx[unk_token] = 1  # Unknown words
        self._word2idx[pad_token] = 0  # Padding
        # Vocabulary Key:token_index -> Value:word
        self._idx2word = {i: w for w, i in self._word2idx.items()}

        tags = list(set(all_datasets["NER_Tag"].values))
        self._n_tags = len(tags)
        self._tag2idx = {t: i + 1 for i, t in enumerate(tags)}
        self._tag2idx[pad_token] = 0
        # Vocabulary Key:tag_index -> Value:Label/Tag
        self._idx2tag = {i: w for w, i in self._tag2idx.items()}

        X_per_subject, y_per_subject = [], []
        for ner_dataset in ner_datasets:
            # Store the (word,pos,tag) list for each sentences in the sentences list
            agg_func = lambda s: [[w, p, t] for w, p, t in \
                                  zip(s["Word"].values.tolist(), s['POS'].values.tolist(),
                                      s["NER_Tag"].values.tolist())]
            sentences_pos_tags = ner_dataset.groupby("Sentence #").apply(agg_func)

            X, y = self._transform_to_format(sentences_pos_tags)
            X_per_subject.append(X)
            y_per_subject.append(y)

        return np.asarray(X_per_subject), np.asarray(y_per_subject)

    def load_model(self, subjects=None, fold=0):
        if subjects is not None:
            model_path = self._model_base_path + '_'.join([str(s) for s in subjects]) + '_' + self._name + '_' + str(
                fold) + '.pkl'
        else:
            model_path = self._model_base_path + self._name + '_' + str(fold) + '.pkl'

        if path.isfile(model_path):
            print("Loading", model_path)
            return spacy.load(model_path)

        return None

    def save_model(self, trained_model, subjects=None, fold=0):
        if self._overwrite:
            return False

        if subjects is not None:
            model_path = self._model_base_path + '_'.join([str(s) for s in subjects]) + '_' + self._name + '_' + str(
                fold) + '.pkl'
        else:
            model_path = self._model_base_path + self._name + '_' + str(fold) + '.pkl'

        print("Saving", model_path)

        model.to_disk(model_path)

    def get_model_architecture(self):
        pass

    def _compute_performance(self, trained_model, data, performance_dict=None):
        scorer = Scorer()
        for input_, annot in data:
            doc_gold_text = trained_model.make_doc(input_)
            gold = GoldParse(doc_gold_text, entities=annot['entities'])
            pred_value = trained_model(input_)
            scorer.score(pred_value, gold)
        results = scorer.scores

        precision = results['ents_p']
        recall = results['ents_r']
        f1 = results['ents_f']
        accuracy = 0.0

        if not performance_dict:
            performance_dict = {
                'Precision': float(0),
                'Recall': float(0),
                'F1': float(0),
                'Accuracy': float(0),
                'Entities': {}
            }
            for label in results['ents_per_type'].keys():
                performance_dict['Entities'][label] = dict()
                performance_dict['Entities'][label]['Precision'] = float(0)
                performance_dict['Entities'][label]['Recall'] = float(0)
                performance_dict['Entities'][label]['F1'] = float(0)

        performance_dict['Precision'] += precision
        performance_dict['Recall'] += recall
        performance_dict['F1'] += f1
        performance_dict['Accuracy'] += accuracy
        print("Precision", precision)
        print("Recall", recall)
        print("F1", f1)
        print("Accuracy", accuracy)
        for label, res in results['ents_per_type'].items():
            performance_dict['Entities'][label]['Precision'] += res['p']
            performance_dict['Entities'][label]['Recall'] += res['r']
            performance_dict['Entities'][label]['F1'] += res['f']
            print("Entity", label, "Precision", res['p'], \
                  "Recall", res['r'], "F1", res['f'])
        return performance_dict

    def _print_performance(self, fold, performance_dict, name):
        if not performance_dict:
            return
        print("\n\nSummary: " + name + ", Fold: " + str(fold))
        precision = performance_dict['Precision'] / self._k_cross_validation
        recall = performance_dict['Recall'] / self._k_cross_validation
        f1 = performance_dict['F1'] / self._k_cross_validation
        print("Precision", precision)
        print("Recall", recall)
        print("F1", f1)
        entities_dict = performance_dict['Entities']
        for entity, _ in entities_dict.items():
            precision = entities_dict[entity]['Precision'] / self._k_cross_validation
            recall = entities_dict[entity]['Recall'] / self._k_cross_validation
            f1 = entities_dict[entity]['F1'] / self._k_cross_validation

            print('Entity', entity, \
                  'Precision', precision, \
                  'Recall', recall, \
                  'F1', f1)
