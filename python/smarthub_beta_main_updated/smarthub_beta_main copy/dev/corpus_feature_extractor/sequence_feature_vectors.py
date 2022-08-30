import numpy as np
from keras.preprocessing.sequence import pad_sequences
from keras.preprocessing.text import Tokenizer
from scipy.sparse.csr import csr_matrix


class SequenceFeatureVectors:
    def __init__(self, feature_extractor):
        self.feature_extractor = feature_extractor

    def extract(self,
                corpus_path,
                tokenize=False,
                include_setup=True,
                include_request=True,
                include_conclusion=True,
                include_surrounding=True,
                include_unigrams=True,
                include_tag=True,
                include_pos=True,
                include_dep=True,
                include_tag_unigrams=True,
                include_pos_unigrams=True,
                include_dep_unigrams=True,
                include_avg_word_embeddings=True,
                include_utt_length=True,
                include_sentiment=True,
                include_number_of_slots=True,
                include_number_of_non_modal_verbs=True,
                include_number_of_wh_words=True,
                max_sequence_length=30,
                seed=7,
                IGNORE_CLASSES=['appearance', 'big high level question'],
                MERGE_CLASSES=['createvis', 'modifyvis'],
                is_corpus_json=False,
                total_versions=50):

        corpus = self.feature_extractor.get_corpus(
            corpus_path=corpus_path,
            tokenize=tokenize,
            include_setup=include_setup,
            include_request=include_request,
            include_conclusion=include_conclusion,
            is_corpus_json=is_corpus_json,
            total_versions=total_versions)

        all_subject_names, all_utterances, all_features, all_utterance_types, \
        all_utterance_types_sequence, subject_name_by_index, \
        subject_name_by_sequence = \
            self.feature_extractor.create_context_features(
                corpus=corpus,
                include_surrounding=include_surrounding,
                include_unigrams=include_unigrams,
                include_tag=include_tag,
                include_pos=include_pos,
                include_dep=include_dep,
                include_tag_unigrams=include_tag_unigrams,
                include_pos_unigrams=include_pos_unigrams,
                include_dep_unigrams=include_dep_unigrams,
                IGNORE_CLASSES=['appearance', 'big high level question'],
                MERGE_CLASSES=['createvis', 'modifyvis'])

        token_split = ';'
        tokenizer = Tokenizer(split=token_split)

        X_raw = []
        X_utterances = []
        y_raw = []
        y_raw_sequence = all_utterance_types_sequence

        context_features = zip(all_subject_names, all_utterances, all_features, all_utterance_types)
        for subject_name, utterances, features, utterance_type in context_features:

            if utterance_type in IGNORE_CLASSES:
                continue

            X_utterances.append(utterances)
            X_raw.append(token_split.join(features))

            if utterance_type in MERGE_CLASSES:
                y_raw.append('merged')
            else:
                y_raw.append(utterance_type)

        CLASSES = np.unique(y_raw)
        #tag_to_index = {str(CLASSES[i]): i + 1 for i in range(len(CLASSES))}
        #tag_to_index['PAD'] = 0
        tag_to_index = {str(CLASSES[i]): i for i in range(len(CLASSES))}
        index_to_tag = {idx: tag for tag, idx in tag_to_index.items()}
        y = np.asarray([tag_to_index[i] for i in y_raw])

        tokenizer.fit_on_texts(X_raw)
        X_indexed_sequences = tokenizer.texts_to_sequences(X_raw)
        X = pad_sequences(X_indexed_sequences, maxlen=max_sequence_length)

        word_to_index = tokenizer.word_index
        word_to_index['UNK'] = 0
        index_to_word = {value: key for key, value in word_to_index.items()}

        np.random.seed(seed)
        vocab_size = len(word_to_index)
        embedding_weights = self.feature_extractor.get_embedding_weights_by_index(vocab_size= \
                                                                                      vocab_size,
                                                                                  word_to_index=word_to_index)

        return subject_name_by_index, subject_name_by_sequence, \
               X_raw, y_raw, y_raw_sequence, embedding_weights, \
               index_to_word, word_to_index, \
               vocab_size, CLASSES, X_utterances, csr_matrix(X), y, \
               tokenizer, tag_to_index, index_to_tag
