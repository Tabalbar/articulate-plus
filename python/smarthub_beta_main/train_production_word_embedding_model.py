import os
os.environ['CUDA_VISIBLE_DEVICES'] = '0'
os.environ["OMP_NUM_THREADS"] = '4'
os.environ["OPENBLAS_NUM_THREADS"] = '5'
os.environ["MKL_NUM_THREADS"] = '6'
os.environ["VECLIB_MAXIMUM_THREADS"] = '4'
os.environ["NUMEXPR_NUM_THREADS"] = '6'
os.environ["NUMEXPR_NUM_THREADS"] = '5'

import time
import gensim
from os import path

from dev.corpus_feature_extractor.corpus_feature_extractor_utils import CorpusFeatureExtractorUtils
from dev.data_extractor.data_extraction_paths import DataExtractionPaths
from dev.text_tokenizer_pipeline.text_processing_utils import TextProcessingUtils
from model_paths import ModelPaths


start_time = time.time()


class Data:
    def __init__(self, tokenizer, corpus):
        self.tokenizer = tokenizer
        # self.corpora = corpora
        self.corpus = corpus

    def __iter__(self):
        # for corpus in self.corpora:
        for doc, index in self.tokenizer.pipe(read_corpus(corpus=corpus),
                                              batch_size=20000, as_tuples=True):
            for sent in doc.sents:
                sent_tokens = [token.text for token in sent]
                if len(sent_tokens) == 0:
                    continue

                yield sent_tokens


INPUT_CORPORA = DataExtractionPaths.ALL_TEXT_DATA_PATHS
TOKENIZED_CORPORA = DataExtractionPaths.ALL_TOKENIZED_PATHS

print("PROCESSING ON CORPORA", '\n'.join(INPUT_CORPORA))
print("TOKENIZING TO CORPORA", '\n'.join(TOKENIZED_CORPORA))


def read_corpus(corpus):
    print("Loading input corpus " + corpus)
    corpus_name = corpus.split('/')[-1]
    index = 0
    iter_time = time.time()
    with open(corpus, 'rt') as corpus_reader:
        for text in corpus_reader:
            if 'wikipedia' in corpus_name:
                processed_text = TextProcessingUtils.clean_text(text=text, \
                                                                mask_digits=True, filter_wiki_subtitles=True,
                                                                lowercase=True, \
                                                                remove_punctuation=True)
            else:
                processed_text = TextProcessingUtils.clean_text(text=text, \
                                                                mask_digits=True, lowercase=True,
                                                                remove_punctuation=True)
            if index % 40000 == 0:
                print("Completed processing " + str(index) + " lines")
                elapsed_time = time.time() - iter_time
                print("Elapsed Time [" + time.strftime( \
                    "%H:%M:%S", time.gmtime(elapsed_time)) + "]")
            # iter_time = time.time()
            yield (processed_text, index)
            index += 1


print("Started extracting from corpora")
tokenizer = CorpusFeatureExtractorUtils.get_context_based_corpus_entity_extractor() \
    .get_tokenizer()

for index in range(len(INPUT_CORPORA)):
    corpus = INPUT_CORPORA[index]
    tokenized_corpus = TOKENIZED_CORPORA[index]

    if path.exists(tokenized_corpus):
        print("Already tokenized " + corpus + " to " + tokenized_corpus)
        continue

    print("Started tokenizing from corpora " + corpus)
    data = Data(tokenizer=tokenizer, corpus=read_corpus(corpus))

    print("Started writing tokens to text file " + tokenized_corpus)
    tokenized_corpus_file = open(tokenized_corpus, 'a+')
    for sent_tokens in data:
        tokenized_corpus_file.write(';'.join(sent_tokens) + '\n')
    print("Completed writing tokens to text file " + tokenized_corpus)

    print("Completed tokenizing from corpus " + corpus)


class TokenizedData:
    def __init__(self, paths):
        self.paths = paths

    def __iter__(self):
        for path in self.paths:
            with open(path, 'rt') as f:
                for text in f:
                    result = []
                    for token in text.split(';'):
                        processed_token = token.strip()
                        processed_token = processed_token.replace("-", " ")
                        if processed_token.isalnum() or ' ' in processed_token:
                            result.append(processed_token)
                    yield result


print("Started training skipgram model")
tokenized_data = TokenizedData(TOKENIZED_CORPORA)
model = gensim.models.Word2Vec(tokenized_data, size=100, window=10, min_count=5, workers=10)
print("Completed training skipgram model")

print("Started saving skipgram model")
model.save(ModelPaths.WORD_EMBEDDING_MODELS_DIR + 'word2vec.100d.chicagocrimevis.pkl')
print("Completed saving skipgram model")

elapsed_time = time.time() - start_time
print("ELAPSED TIME", elapsed_time)
time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
print("Completed extracting from corpora")
