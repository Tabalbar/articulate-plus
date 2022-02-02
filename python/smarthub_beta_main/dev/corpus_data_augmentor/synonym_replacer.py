from ..data_extractor.resource_lookup_utils import ResourceLookupUtils

import numpy as np


class SynonymReplacer:
    def __init__(self, corpus_entity_extractor, use_wordnet=False, use_index=True):
        self.corpus_entity_extractor = corpus_entity_extractor
        self.nlp = self.corpus_entity_extractor.get_tokenizer()
        self.embedding_model = self.corpus_entity_extractor.get_embedding_model()
        self.use_wordnet = use_wordnet

        self.annoy_index = None
        if use_index:
            print("Creating word embedding indexer")
            from gensim.similarities.index import AnnoyIndexer
            self.embedding_model.init_sims()
            self.annoy_index = AnnoyIndexer(self.embedding_model, 100)
            print("Completed creating word embedding indexer")

    def get_valid_candidate_indices(self, utterance):
        candidate_indices = []
        if self.use_wordnet:
            for idx, token in enumerate(utterance):
                if token._.is_entity:
                    continue
                if token.pos_ not in ['NOUN', 'PROPN', 'VERB', 'ADJ', 'ADV']:
                    continue
                if token.is_stop or token.text == 'safe' or token.text == 'heat' or token.text == 'hot':
                    continue
                if token.dep_ == 'aux':
                    continue
                if token.text == 'am' or token.text == 'pm':
                    continue

                candidate_indices.append(idx)

            return candidate_indices

        for idx, token in enumerate(utterance):
            if token._.is_entity:
                continue
            if token.pos_ not in ['NOUN', 'PROPN', 'VERB', 'ADJ', 'ADV']:
                continue
            if token.is_stop or token.text == 'heat' or token.text == 'hot':
                continue
            if token.dep_ == 'aux':
                continue
            if token.text == 'am' or token.text == 'pm':
                continue

            if token.text not in self.embedding_model:
                continue

            candidate_indices.append(idx)

        return candidate_indices

    def get_synonyms_using_nearest_embedding_neighbor(self, utterance, candidate_indices):
        synonym_replaced_utterance = []
        for idx, token in enumerate(utterance):
            if idx not in candidate_indices:
                synonym_replaced_utterance.append(token.text)
                continue

            if self.annoy_index is None:
                near_token = np.random.choice([synonym for synonym, sim in \
                                               self.embedding_model.wv.most_similar(token.text, topn=10)])
                # print("Found synonym",near_token,"for token",token.lemma_,"pos",token.pos_,'tag',token.tag_,'dep',
                # token.dep_)
                synonym_replaced_utterance.append(near_token)
                continue

            near_token = np.random.choice([synonym for synonym, sim in \
                                           self.embedding_model.most_similar(token.text, topn=10,
                                                                             indexer=self.annoy_index)])
            # print("Found synonym",near_token,"for token",token.lemma_,"pos",token.pos_,'tag',token.tag_,'dep',
            # token.dep_)
            synonym_replaced_utterance.append(near_token)

        return synonym_replaced_utterance

    def get_synonyms_using_wordnet(self, utterance, candidate_indices):
        synonym_replaced_utterance = []
        for idx, token in enumerate(utterance):
            if idx not in candidate_indices:
                synonym_replaced_utterance.append(token.text)
                continue

            synonyms = ResourceLookupUtils.get_wordnet_synonyms(phrase=token.lemma_, pos=token.pos_)
            hyponyms = ResourceLookupUtils.get_wordnet_hyponyms(phrase=token.lemma_, pos=token.pos_)
            if synonyms is None:
                synonym_replaced_utterance.append(token.text)
                # print("Found synonym",near_token,"for token",token.lemma_,"pos",token.pos_,'tag',token.tag_,'dep',
                # token.dep_)
                continue
            if hyponyms is not None:
                synonyms.update(hyponyms)
            print("PICK RANDOM SYN", synonyms)
            near_token = np.random.choice(list(synonyms))
            # print("Found synonym",near_token,"for token",token.lemma_,"pos",token.pos_,'tag',token.tag_,'dep',
            # token.dep_)
            synonym_replaced_utterance.append(near_token)
        return synonym_replaced_utterance

    def get_synonym_replaced_utterances(self, utterances, synonym_limit=3):
        for utt_idx_id, utterance in enumerate(utterances):
            if utt_idx_id == 0:
                yield utterance.text
                continue

            candidate_indices = self.get_valid_candidate_indices(utterance=utterance)

            if len(candidate_indices) < synonym_limit:
                adjusted_synonym_limit = len(candidate_indices)
            else:
                adjusted_synonym_limit = synonym_limit

            if adjusted_synonym_limit == 0:
                continue

            candidate_indices = sorted(np.random.choice(candidate_indices, adjusted_synonym_limit, replace=False))

            if self.use_wordnet:
                synonym_replaced_utterance = self.get_synonyms_using_wordnet(utterance=utterance,
                                                                             candidate_indices=candidate_indices)
            else:
                synonym_replaced_utterance = self.get_synonyms_using_nearest_embedding_neighbor(utterance=utterance,
                                                                                                candidate_indices=candidate_indices)

            yield ' '.join(synonym_replaced_utterance)
