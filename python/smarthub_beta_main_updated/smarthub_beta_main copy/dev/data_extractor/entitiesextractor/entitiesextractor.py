import json
from collections import defaultdict
import numpy as np
from sklearn.metrics import pairwise_distances_argmin_min

from model_paths import ModelPaths
from .entity import Entity
from ..resource_lookup_utils import ResourceLookupUtils
from ...binning import Binning
from ...embeddings import EmbeddingFactory
from ...text_tokenizer_pipeline.text_processing_utils import TextProcessingUtils


class EntitiesExtractor:
    def __init__(self, embedding_model_path, embedding_model_name):
        self.entities = dict()

        self.bins = None
        self.bin_names = None

        self.terms = set()
        self.synonyms = set()
        self.hyponyms = set()
        self.data_attributes = set()
        self.names = set()
        self.values = set()

        self.knowledgebase = []

        self.regular_expression_entities = []

        self.term_to_entity_mapping = dict()

        #model_name = 'word2vec.100d.chicagocrimevis'
        embedding_config = {'use_embedding': 'word2vec',
                            'dims': 100,
                            'embedding_model_path': embedding_model_path,
                            'embedding_model_name': embedding_model_name,
                            'train': None,
                            'verbose': True}
        self.embedding_dimensions = embedding_config['dims']
        embedding_model_container = EmbeddingFactory.build(embedding_config)
        embedding_model_container.load(file_name=embedding_model_path + embedding_model_name + '.pkl')
        self.embedding_model = embedding_model_container
        self.name_embeddings = None
        self.value_embeddings = None

    @staticmethod
    def extract_synonyms_from_external_resources(phrase):
        babelnet_synonyms = ResourceLookupUtils.get_babelnet_synonyms(phrase)
        wordnet_synonyms = ResourceLookupUtils.get_wordnet_synonyms(phrase)

        synonyms = set()
        if babelnet_synonyms is not None:
            synonyms.update(babelnet_synonyms)
        if wordnet_synonyms is not None:
            synonyms.update(wordnet_synonyms)
        if len(synonyms) == 0:
            return None

        return synonyms

    @staticmethod
    def extract_hyponyms_from_external_resources(phrase):
        hyponyms = ResourceLookupUtils.get_wordnet_hyponyms(phrase)
        return hyponyms

    @staticmethod
    def extract_value_when_data_attribute_specified(slotvalue):
        tokens = slotvalue.split('->')
        token_values = tokens[0].split('&&&')

        return [(token_value, ' '.join(token_value.split('REGEXP')).strip()) for token_value in token_values]

    @staticmethod
    def extract_data_attribute_when_specified(slotvalue):
        tokens = slotvalue.split('->')
        if tokens[1] == 'NULL':
            return None
        return tokens[1]

    @staticmethod
    def extract_value(slotvalue):
        if '->' in slotvalue:
            return EntitiesExtractor.extract_value_when_data_attribute_specified(slotvalue)
        return [(slotvalue, slotvalue)]

    @staticmethod
    def extract_data_attribute(slotvalue):
        if '->' in slotvalue:
            return EntitiesExtractor.extract_data_attribute_when_specified(slotvalue)
        return slotvalue

    def add_entity(self, entity):
        if entity.get_name() not in self.entities:
            self.entities[entity.get_name()] = dict()

        if entity.get_value() not in self.entities[entity.get_name()]:
            self.entities[entity.get_name()][entity.get_value()] = None

        self.entities[entity.get_name()][entity.get_value()] = entity

        entity_data = dict()
        entity_data['name'] = entity.get_name()
        entity_data['value'] = entity.get_value()
        entity_data['synonyms'] = entity.get_synonyms()
        entity_data['hyponyms'] = entity.get_hyponyms()
        entity_data['data_attribute'] = entity.get_data_attribute()
        entity_data['isregularexpression'] = entity.get_is_regular_expression()
        self.knowledgebase.append(entity_data)

        if entity.get_value() is not None:
            if entity.get_value().lower() not in self.term_to_entity_mapping:
                self.term_to_entity_mapping[entity.get_value().lower()] = []
            self.term_to_entity_mapping[entity.get_value().lower()].append(entity)

        if entity.get_is_regular_expression():
            self.regular_expression_entities.append(entity)

        if entity.get_name().lower() not in self.term_to_entity_mapping:
            self.term_to_entity_mapping[entity.get_name().lower()] = []
        if entity not in self.term_to_entity_mapping[entity.get_name().lower()]:
            self.term_to_entity_mapping[entity.get_name().lower()].append(entity)

        if entity.get_data_attribute() is not None:
            if entity.get_data_attribute().lower() not in self.term_to_entity_mapping:
                self.term_to_entity_mapping[entity.get_data_attribute().lower()] = []
            if entity not in self.term_to_entity_mapping[entity.get_data_attribute().lower()]:
                self.term_to_entity_mapping[entity.get_data_attribute().lower()].append(entity)

        if entity.get_synonyms() is not None:
            for synonym in entity.get_synonyms():
                if synonym.lower() not in self.term_to_entity_mapping:
                    self.term_to_entity_mapping[synonym.lower()] = []
                if entity not in self.term_to_entity_mapping[synonym.lower()]:
                    self.term_to_entity_mapping[synonym.lower()].append(entity)

        if entity.get_hyponyms() is not None:
            for hyponym in entity.get_hyponyms():
                if hyponym.lower() not in self.term_to_entity_mapping:
                    self.term_to_entity_mapping[hyponym.lower()] = []
                if entity not in self.term_to_entity_mapping[hyponym.lower()]:
                    self.term_to_entity_mapping[hyponym.lower()].append(entity)

    def store_ontology(self, output_target_file):
        with open(output_target_file, 'w') as f:
            json.dump(self.entities, f, indent=4, sort_keys=True)

    def get_ontology(self):
        return self.entities

    def extract_from_ontology(self, input_source_file):
        with open(input_source_file) as f:
            ontology = json.load(f)

        for index in range(len(ontology['slotname'])):
            slotname = ontology['slotname'][index]
            print("Processing slot " + str(slotname))

            parent_entity = Entity(slotname, None, slotname)
            phrase = slotname
            synonyms = EntitiesExtractor.extract_synonyms_from_external_resources(phrase)
            if synonyms is not None:
                synonyms = [TextProcessingUtils.lemmatize_text(synonym) for synonym in synonyms \
                            if TextProcessingUtils.is_text_in_ascii(synonym) and len(synonym) > 1]
                print("Extracted " + str(len(synonyms)) + " total synonyms for phrase " + str(phrase))
                parent_entity.add_synonyms(synonyms)
                self.terms.update(synonyms)
                self.synonyms.update(synonyms)

            '''hyponyms = EntitiesExtractor.extract_hyponyms_from_external_resources(phrase)
            if hyponyms is not None:
                hyponyms = [TextProcessingUtils.lemmatize_text(hyponym) for hyponym in hyponyms \
                    if TextProcessingUtils.is_text_in_ascii(hyponym) and len(hyponym)>1]
                parent_entity.add_hyponyms(hyponyms)
                self.terms.update(hyponyms)
                self.hyponyms.update(hyponyms)'''

            self.add_entity(parent_entity)
            self.terms.add(slotname)
            self.names.add(slotname)

            slotvalues = ontology['slotvalue'][index]
            print("Processing slot values " + str(slotvalues))
            for slotvalue in slotvalues.split(';'):
                data_attribute = EntitiesExtractor.extract_data_attribute(slotvalue)

                if data_attribute is not None:
                    self.terms.add(data_attribute)
                    self.data_attributes.add(data_attribute)

                for unprocessed_value, processed_value in EntitiesExtractor.extract_value(slotvalue):
                    if processed_value == 'NULL':
                        continue

                    child_entity = Entity(slotname, processed_value, data_attribute)

                    phrase = processed_value
                    synonyms = EntitiesExtractor.extract_synonyms_from_external_resources(phrase)
                    if synonyms is not None:
                        synonyms = [TextProcessingUtils.lemmatize_text(synonym) for synonym in synonyms \
                                    if TextProcessingUtils.is_text_in_ascii(synonym) and len(synonym) > 1]
                        print("Extracted " + str(len(synonyms)) + " total synonyms for phrase " + str(phrase))
                        child_entity.add_synonyms(synonyms)
                        self.terms.update(synonyms)
                        self.synonyms.update(synonyms)

                    '''hyponyms = EntitiesExtractor.extract_hyponyms_from_external_resources(phrase)
                    if hyponyms is not None:
                        hyponyms = [TextProcessingUtils.lemmatize_text(hyponym) for hyponym in hyponyms \
                            if TextProcessingUtils.is_text_in_ascii(hyponym) and len(hyponym)>1]
                        child_entity.add_hyponyms(hyponyms)
                        self.terms.update(hyponyms)
                        self.hyponyms.update(hyponyms)'''

                    if 'REGEXP' in unprocessed_value:
                        child_entity.set_is_regular_expression(True)
                    else:
                        self.terms.add(processed_value)
                        self.values.add(processed_value)
                        child_entity.set_is_regular_expression(False)
                    self.add_entity(child_entity)

    def get_knowledgebase(self):
        return self.knowledgebase

    def store_knowledgebase(self, output_target_file):
        with open(output_target_file, 'w') as f:
            json.dump(self.knowledgebase, f, indent=4, sort_keys=True)

    def extract_from_knowledgebase(self, input_target_file):
        with open(input_target_file, 'rt') as f:
            knowledgebase = json.load(f)

        self.entities = dict()
        for entity in knowledgebase:
            name, value, synonyms, hyponyms, data_attribute, is_regular_expression = \
                entity['name'], entity['value'], entity['synonyms'], entity['hyponyms'], \
                entity['data_attribute'], entity['isregularexpression']
            entity = Entity(name, value, data_attribute)

            if synonyms and len(synonyms) > 0:
                synonyms = [TextProcessingUtils.lemmatize_text(synonym) for synonym in synonyms \
                            if TextProcessingUtils.is_text_in_ascii(synonym) and len(synonym) > 1]

                entity.add_synonyms(synonyms)
                self.synonyms.update(synonyms)
                self.terms.update(synonyms)

            if hyponyms and len(hyponyms) > 0:
                hyponyms = [TextProcessingUtils.lemmatize_text(hyponym) for hyponym in hyponyms \
                            if TextProcessingUtils.is_text_in_ascii(hyponym) and len(hyponym) > 1]

                self.hyponyms.update(hyponyms)
                self.terms.update(hyponyms)
                entity.add_hyponyms(hyponyms)

            if data_attribute is not None:
                self.data_attributes.add(data_attribute)
                if not is_regular_expression:
                    self.terms.add(data_attribute)

            entity.set_is_regular_expression(is_regular_expression)

            self.names.add(name)
            self.terms.add(name)

            if name not in self.entities:
                self.entities[name] = dict()

            if isinstance(value, list):
                for item in value:
                    self.values.add(item)
                    if is_regular_expression == False:
                        self.terms.add(item)

                    if item not in self.entities[name]:
                        self.entities[name][item] = None
                    self.entities[name][item] = entity
            else:
                if value is not None:
                    self.values.add(value)

                    if is_regular_expression == False:
                        self.terms.add(value)

                if value not in self.entities[name]:
                    self.entities[name][value] = None
                self.entities[name][value] = entity

            self.add_entity(entity)

        bin_to_embedding = defaultdict(list)
        for name in self.get_all_names():
            values = self.get_matched_values(name, find_closest=False)
            if not values:
                continue
            for value in values:
                bin_to_embedding[name].append((value, self.embedding_model.get_token_embedding(None, value.lower())))
                matched_entities = self.get_matched_entities(value, find_closest=False)
                if not matched_entities:
                    continue
                for matched_entity in matched_entities:
                    synonyms = matched_entity.get_synonyms()
                    if not synonyms:
                        continue
                    for synonym in synonyms:
                        bin_to_embedding[value].append(
                            (synonym, self.embedding_model.get_token_embedding(None, synonym.lower())))

        self.bins = Binning()
        self.bin_names = list(bin_to_embedding.keys())
        for bin_idx, bin_name in enumerate(self.bin_names):
            done = [self.bins.add_to_bin(bin_idx, e[1]) for e in bin_to_embedding[bin_name]]

    def get_all_names(self):
        return self.names

    def get_all_values(self):
        return self.values

    def get_all_reg_exp_resolved_values(self):
        resolved_values = set()
        for value in self.values:
            if not value:
                continue

            if '\\b' in value:
                data_attribute = self.term_to_entity_mapping[value][0].get_data_attribute()
                if data_attribute:
                    resolved_values.add(data_attribute)
            else:
                resolved_values.add(value)
        return resolved_values

    def get_all_synonyms(self):
        return self.synonyms

    def get_all_hyponyms(self):
        return self.hyponyms

    def get_all_data_attributes(self):
        return self.data_attributes

    def get_all_terms(self):
        return self.terms

    def get_all_entities(self):
        return self.entities

    def get_all_regular_expression_entities(self):
        return self.regular_expression_entities

    def get_entity_values(self, name):
        return self.entities[name]

    def get_entity(self, name, value):
        return self.entities[name][value]

    def get_term_to_entity_mapping(self):
        return self.term_to_entity_mapping

    def get_matched_entities(self, term, find_closest=True):
        if not term:
            return None
        if term not in self.term_to_entity_mapping:
            if not find_closest:
                return None
            term = self.get_closest_term(term)
            if not term:
                return None
        return self.term_to_entity_mapping[term]

    def get_is_named_entity_category(self, term, find_closest=True):
        if not term:
            return False
        if term not in self.term_to_entity_mapping:
            if not find_closest:
                return False
            term = self.get_closest_term(term)
            if not term:
                return False

        data = self.term_to_entity_mapping[term]
        if not data:
            return False

        return data[0].get_is_named_entity_category()

    def get_matched_data_attributes(self, term, find_closest=True):
        if not term:
            return None
        if term not in self.term_to_entity_mapping:
            if not find_closest:
                return None
            term = self.get_closest_term(term)
            if not term:
                return None

        data = self.term_to_entity_mapping[term]

        if len(data) > 1:
            return [t.get_data_attribute() for t in data if
                    t.get_data_attribute() and '\\b' not in t.get_data_attribute()][1:]

        target = data[0].get_data_attribute()
        if target in self.term_to_entity_mapping:
            target_data = self.term_to_entity_mapping[target]
            if len(target_data) > 1:
                return [t.get_data_attribute() for t in target_data if
                        t.get_data_attribute() and '\\b' not in t.get_data_attribute()][1:]
            else:
                return [t.get_data_attribute() for t in target_data if
                        t.get_data_attribute() and '\\b' not in t.get_data_attribute()]

        return target

    def get_matched_values(self, term, find_closest=True):
        if not term:
            return None
        if term not in self.term_to_entity_mapping:
            if not find_closest:
                return None
            term = self.get_closest_term(term)
            if not term:
                return None

        data = self.term_to_entity_mapping[term]

        if not data:
            return None

        if len(data) > 1:
            values = []
            for entity in data:
                if entity.get_value() and '\\b' not in entity.get_value():
                    values.append(entity.get_value())
                elif entity.get_data_attribute():
                    values.append(entity.get_data_attribute())
            return values

        target = data[0].get_value()
        if target in self.term_to_entity_mapping:
            values = []
            for entity in self.term_to_entity_mapping[target]:
                if entity.get_value() and '\\b' not in entity.get_value():
                    values.append(entity.get_value())
                elif entity.get_data_attribute():
                    values.append(entity.get_data_attribute())
            return values

        if not target:
            return None

        return [target]

    def get_name(self, term, find_closest=True):
        if not term:
            return None
        if term not in self.term_to_entity_mapping:
            if not find_closest:
                return None
            term = self.get_closest_term(term)
            if not term:
                return None
        return self.term_to_entity_mapping[term][0].get_name()

    def is_data_attribute(self, term, find_closest=True):
        return self.get_matched_data_attributes(term=term, find_closest=find_closest) != []

    def get_data_attribute_name(self, term, find_closest=True):
        name = self.get_name(term=term, find_closest=find_closest)
        if not name:
            return None

        if not self.is_data_attribute(term=name, find_closest=find_closest):
            return None

        return name

    def get_embeddings(self):
        return self.embedding_model

    def get_all_names_embeddings(self):
        if self.name_embeddings:
            return self.name_embeddings

        self.name_embeddings = {t.lower(): (idx, self.embedding_model.get_token_embedding(None, t.lower())) \
                                for idx, t in enumerate(self.get_all_names())}
        return self.name_embeddings

    def get_all_values_embeddings(self):
        if self.value_embeddings:
            return self.value_embeddings

        self.value_embeddings = {t.lower(): (idx, self.embedding_model.get_token_embedding(None, t.lower())) \
                                 for idx, t in enumerate(self.get_all_reg_exp_resolved_values())}
        return self.value_embeddings

    def get_closest_term(self, term, cos_sim_threshold=0.55):
        term_embedding = self.embedding_model.get_token_embedding(None, term).\
            reshape(-1).reshape(-1, self.embedding_dimensions)

        _, closest = pairwise_distances_argmin_min(self.bins.centroids, term_embedding, metric='cosine')
        idx = np.argmin(closest)
        if 1 - closest[idx] >= cos_sim_threshold:
            return self.bin_names[idx]
        return None
