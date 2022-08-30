import os
os.environ['CUDA_VISIBLE_DEVICES'] = '0'
os.environ["OMP_NUM_THREADS"] = '4'
os.environ["OPENBLAS_NUM_THREADS"] = '5'
os.environ["MKL_NUM_THREADS"] = '6'
os.environ["VECLIB_MAXIMUM_THREADS"] = '4'
os.environ["NUMEXPR_NUM_THREADS"] = '6'
os.environ["NUMEXPR_NUM_THREADS"] = '5'

import time

from dev.corpus_feature_extractor.corpus_feature_extractor_utils import CorpusFeatureExtractorUtils
from dev.data_extractor.data_extraction_paths import DataExtractionPaths
from dev.text_tokenizer_pipeline.text_processing_utils import TextProcessingUtils

start_time = time.time()


class Data:
    def __init__(self, tokenizer, corpus):
        self.tokenizer = tokenizer
        self.corpus = corpus

    def __iter__(self):
        for doc, index in self.tokenizer.pipe(read_corpus(corpus=corpus), \
                                              batch_size=20000, as_tuples=True):
            for sent in doc.sents:
                for word in sent:
                    entity = None
                    if word._.entity:
                        entity = word._.entity
                    elif word._.is_entity:
                        entity = 'entity'
                    yield word.text, word.pos_, word.tag_, word.dep_, entity
                yield '\n', '\n', '\n', '\n', '\n'


'''INPUT_CORPORA = [
DataExtractionPaths.CHICAGO_ENCYCLOPEDIA_DATA_PATH,\
DataExtractionPaths.CHICAGO_SUN_TIMES_NEIGHBORHOODS_DATA_PATH,\
DataExtractionPaths.CWB_CHICAGO_DATA_PATH]
DataExtractionPaths.CJP_NEWS_ARTICLES_DATA_PATH]'''
INPUT_CORPORA = [DataExtractionPaths.CHICAGO_ENCYCLOPEDIA_TEXT_DATA_PATH]
IOB_CORPORA = [DataExtractionPaths.CHICAGO_ENCYCLOPEDIA_IOB_PATH]

print("PROCESSING ON CORPORA", '\n'.join(INPUT_CORPORA))
print("TRANSFORMING TO IOB FORMAT FOR CORPORA", '\n'.join(IOB_CORPORA))


def read_corpus(corpus):
    print("Loading input corpus " + corpus)
    corpus_name = corpus.split('/')[-1]
    index = 0
    iter_time = time.time()
    with open(corpus, 'rt') as corpus_reader:
        for text in corpus_reader:
            if 'wikipedia' in corpus_name:
                processed_text = TextProcessingUtils.clean_text(text=text,
                                                                mask_digits=True, filter_wiki_subtitles=True,
                                                                lowercase=False,
                                                                remove_punctuation=False)
            else:
                processed_text = TextProcessingUtils.clean_text(text=text,
                                                                mask_digits=True, lowercase=False,
                                                                remove_punctuation=False)
            if index % 40000 == 0:
                print("Completed processing " + str(index) + " lines")
                elapsed_time = time.time() - iter_time
                print("Elapsed Time [" + time.strftime(
                    "%H:%M:%S", time.gmtime(elapsed_time)) + "]")
            # iter_time = time.time()
            yield (processed_text, index)
            index += 1


print("Started extracting from corpora")
tokenizer = CorpusFeatureExtractorUtils.get_context_based_corpus_entity_extractor() \
    .get_tokenizer()

for index in range(len(INPUT_CORPORA)):
    corpus = INPUT_CORPORA[index]
    iob_corpus = IOB_CORPORA[index]
    print("Started transforming to iob format for corpora " + corpus)
    data = Data(tokenizer=tokenizer, corpus=read_corpus(corpus))

    print("Started writing tokens to text file " + iob_corpus)
    iob_corpus_file = open(iob_corpus, 'a+')
    for word, pos, tag, dep, ner_label in data:
        base_str = pos + ' ' + tag + ' ' + dep
        if word == '\n':
            iob_corpus_file.write('\n')
            continue
        token_str = 'None'
        if ner_label and word:
            tokens = word.split()
            token_str = tokens[0] + ' ' + base_str + ' B-' + ner_label + '\n'
            for token_idx in range(1, len(tokens)):
                token_str += tokens[token_idx] + ' ' + base_str + ' I-' + ner_label + '\n'
        else:
            tokens = word.split()
            token_str = ''
            for token_idx in range(len(tokens)):
                token_str += tokens[token_idx] + ' ' + base_str + ' O\n'
        iob_corpus_file.write(token_str)
    print("Completed writing tokens to text file " + iob_corpus)

    print("Completed transforming to iob format for corpora " + corpus)


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
tokenized_data = TokenizedData(IOB_CORPORA)
