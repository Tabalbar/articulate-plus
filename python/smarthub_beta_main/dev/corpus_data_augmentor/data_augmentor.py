import copy
import numpy as np
import random
from collections import OrderedDict


class DataAugmentor:
    def __init__(self, corpus_entity_extractor, paraphraser=None, slot_replacer=None, synonym_replacer=None,
                 total_versions=10):
        self.nlp = corpus_entity_extractor.get_tokenizer()
        self.paraphraser = paraphraser
        self.slot_replacer = slot_replacer
        self.synonym_replacer = synonym_replacer
        self.context_components = OrderedDict()

        self.total_versions = total_versions

    def add_context_component(self, context_component_type, context_component):
        if context_component_type not in self.context_components:
            self.context_components[context_component_type] = dict()

            for version_id in range(self.total_versions):
                self.context_components[context_component_type][version_id] = []

        context_component_versions = self.apply_versioning(context_component)
        for versions in context_component_versions:
            padded_versions = self.apply_random_padding(versions)

            first_padded_version = padded_versions[0]
            remaining_padded_versions = padded_versions[1:]
            random.shuffle(remaining_padded_versions)
            padded_versions = [first_padded_version] + remaining_padded_versions

            for version_id in range(self.total_versions):
                padded_version = padded_versions[version_id]
                self.context_components[context_component_type][version_id].append(padded_version)

    def get_context_components_version(self, version_id):
        context_component_versions = dict()
        for context_component_type, version_id_mapping in self.context_components.items():
            if context_component_type not in context_component_versions:
                context_component_versions[context_component_type] = None
            context_component_versions[context_component_type] = version_id_mapping[version_id]
        return context_component_versions

    def get_context_components(self):
        return self.context_components

    def apply_context_component_versioning(self, context_component):
        utterance = context_component['utterance'][3]

        if self.paraphraser is not None:
            versioned_utterances = self.paraphraser.get_paraphrases(utterance=utterance, number_of_paraphrases=20)
            # versioned_utterances = self.nlp.pipe(versioned_utterances, batch_size=1000)
            versioned_utterances = [self.nlp(versioned_utterance) for versioned_utterance in \
                                    versioned_utterances]
        else:
            # versioned_utterances = self.nlp.pipe([utterance])
            versioned_utterances = [self.nlp(utterance)]

        if self.slot_replacer is not None:
            versioned_utterances = self.slot_replacer.get_slot_replaced_utterances(utterances=versioned_utterances,
                                                                                   slot_limit=3,
                                                                                   use_all_combinations=True,
                                                                                   total_versions=self.total_versions)

        versioned_utterances = list(versioned_utterances)
        start_version = versioned_utterances[0]
        remaining_versions = versioned_utterances[1:]
        random.shuffle(remaining_versions)
        versioned_utterances = [start_version] + remaining_versions
        versioned_utterances = versioned_utterances[:3 * self.total_versions]

        if self.synonym_replacer is not None:
            # versioned_utterances = self.nlp.pipe(versioned_utterances, batch_size=1000)
            versioned_utterances = [self.nlp(versioned_utterance) for versioned_utterance in \
                                    versioned_utterances]
            versioned_utterances = self.synonym_replacer.get_synonym_replaced_utterances(
                utterances=versioned_utterances, synonym_limit=4)

        all_context_component_cpy = []
        for versioned_utterance in versioned_utterances:
            context_component_cpy = copy.deepcopy(context_component)
            context_component_cpy['utterance'][3] = versioned_utterance
            all_context_component_cpy.append(context_component_cpy)
        return all_context_component_cpy

    def apply_versioning(self, context_components):
        all_context_component_versions = []
        for context_component in context_components:
            context_component_versions = self.apply_context_component_versioning(
                context_component.get_context_component_as_json())
            all_context_component_versions.append(context_component_versions)
        return all_context_component_versions

    def apply_random_padding(self, context_component_versions):
        total_versions = self.total_versions

        actual_total_versions = len(context_component_versions)

        # total number of versions required to be created
        version_diff = total_versions - actual_total_versions

        # if there is enough data such that new versions are not required to be created
        if version_diff == 0 or version_diff < 0:
            return [context_component_versions[0]] + \
                   list(np.random.choice(context_component_versions[1:], total_versions - 1, replace=False))

        # there is not enough data, hence need to create some more data.
        # if the amount of data required to be created is less than the current amount of data, then
        # simply add the version_diff amount
        if version_diff < actual_total_versions:
            context_component_versions += \
                list(np.random.choice(context_component_versions, version_diff, replace=False))
            return context_component_versions

        # there is not enough data, hence need to create some more data.
        # if the amount of data required to be created is more than the current amount of data, then
        # iteratively add more and more data.
        while actual_total_versions < total_versions:
            if 2 * actual_total_versions > total_versions:
                actual_total_versions = total_versions - actual_total_versions

            context_component_versions += \
                list(np.random.choice(context_component_versions, actual_total_versions, replace=False))
            actual_total_versions = len(context_component_versions)

        return context_component_versions
