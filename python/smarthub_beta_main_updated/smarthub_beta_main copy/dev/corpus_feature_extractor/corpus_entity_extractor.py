from abc import ABCMeta, abstractmethod
import spacy
from spacy.language import Language

from ..corpus_extractor.extractor import Extractor
from ..corpus_extractor.utterance_processing_utils import UtteranceProcessingUtils
from ..text_tokenizer_pipeline.entity_compound_filter import EntityCompoundFilter
from ..text_tokenizer_pipeline.entity_dependency_filter import EntityDependencyFilter
from ..text_tokenizer_pipeline.entity_pos_and_temporal_filter import EntityPOSAndTemporalFilter
from ..text_tokenizer_pipeline.text_processing_utils import TextProcessingUtils
from ..text_tokenizer_pipeline.text_tokenizer import TextTokenizer


class CorpusEntityExtractor(metaclass=ABCMeta):
    __metaclass__ = ABCMeta

    def __init__(self, named_entities, regular_expressions, entity_lookup):
        super().__init__()

        self.entity_nlp = spacy.load('en_core_web_sm')
        self.non_entity_nlp = spacy.load('en_core_web_sm')

        embedding_model_container = entity_lookup.get_embeddings()
        self.embedding_model = embedding_model_container
        keys = []
        for idx in range(len(embedding_model_container.embedding_model.wv.vocab)):
            keys.append(embedding_model_container.embedding_model.wv.index2word[idx])
        self.entity_nlp.vocab.vectors = spacy.vocab.Vectors(data=embedding_model_container.embedding_model.wv.syn0,
                                                            keys=keys)
        self.non_entity_nlp.vocab.vectors = spacy.vocab.Vectors(data=embedding_model_container.embedding_model.wv.syn0,
                                                                keys=keys)

        print('Loaded word embeddings of size', self.entity_nlp.vocab.vectors.shape)

        @Language.factory('entitycompoundfilter')
        def create_entity_compound_filter(nlp, name):
            return EntityCompoundFilter()

        @Language.factory('entitydependencyfilter')
        def create_entity_dependency_filter(nlp, name):
            return EntityDependencyFilter()

        @Language.factory('entityposandtemporalfilter')
        def create_pos_and_temporal_filter(nlp, name):
            return EntityPOSAndTemporalFilter()

        self.entity_nlp.remove_pipe('ner')
        self.entity_nlp.add_pipe(factory_name='entityposandtemporalfilter', after='attribute_ruler')
        self.entity_nlp.add_pipe(factory_name='entitycompoundfilter', after='entityposandtemporalfilter')
        self.entity_nlp.add_pipe(factory_name='entitydependencyfilter', after='entitycompoundfilter')

        self.entity_nlp.tokenizer = TextTokenizer(named_entities=named_entities,
                                                  regular_expressions=regular_expressions, entity_lookup=entity_lookup,
                                                  vocab=self.entity_nlp.vocab)

        self.entity_lookup = entity_lookup

        #utt = ' '.join('so;can;you;tell;me;the;the;day;of;the;week;where;the;crime;is;maximum'.split(';'))
        #utt = 'so the crime rate is maximum between 12 pm and 6 pm'
        #print("TEST",[(t.text, t._.entity) for t in self.entity_nlp(utt)])
        #print("entity_nlp address", self.entity_nlp)
        #print("non_entity_nlp address", self.non_entity_nlp)

    @staticmethod
    def preprocess_utterances_from_annotations(annotations):
        utterances = []
        for annotation in annotations:
            utterance = UtteranceProcessingUtils.clean_utterance(
                TextProcessingUtils.clean_text(
                    text=annotation.get_utterance().get_utterance_attribute(), lowercase=True,
                    remove_punctuation=True), remove_hyphens=True)
            utterances.append(utterance)
        return utterances

    def get_tokens(self, utterances, tokenize=True):
        if tokenize:
            return self.entity_nlp.pipe(utterances, batch_size=32)
        else:
            return self.non_entity_nlp.pipe(utterances, batch_size=32)

    @abstractmethod
    def get_subject_tokens(self, contexts, tokenize=True,
                           include_setup=True, include_request=True, include_conclusion=True):
        raise NotImplementedError()

    def extract(self, corpus_path, tokenize=True, include_setup=True, include_request=True, include_conclusion=True,
                is_corpus_json=False, total_versions=50):
        if is_corpus_json:
            data = Extractor.extract_from_json(corpus_path=corpus_path,
                                               total_versions=total_versions, process_refexps=False)
        else:
            data = Extractor.extract(corpus_path=corpus_path, process_refexps=False)

        subject_tokens_by_context = []
        for subject_name, contexts in data:
            subject_tokens = \
                self.get_subject_tokens(
                    contexts=contexts,
                    tokenize=tokenize,
                    include_setup=include_setup,
                    include_request=include_request,
                    include_conclusion=include_conclusion)
            subject_tokens_by_context.append((subject_name, subject_tokens))
        return subject_tokens_by_context

    def get_tokenizer(self):
        return self.entity_nlp

    def get_embedding_model(self):
        return self.embedding_model

    def get_embeddings(self):
        return self.entity_nlp.vocab.vectors

    def get_entity_lookup(self):
        return self.entity_lookup
