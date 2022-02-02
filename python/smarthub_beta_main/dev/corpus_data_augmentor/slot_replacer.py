import itertools

import numpy as np


class SlotReplacer:
    def __init__(self, corpus_entity_extractor):
        self.corpus_entity_extractor = corpus_entity_extractor
        self.nlp = self.corpus_entity_extractor.get_tokenizer()

    def get_all_entity_slots(self, utterance):
        for token in utterance:
            if token._.entity_value:
                yield token._.entity_value

    def get_all_entity_slot_combinations(self, utterance, use_all_combinations=False, slot_limit=4, total_versions=10):
        candidate_entity_slots = list(self.get_all_entity_slots(utterance))
        total_candidates = len(candidate_entity_slots)
        if total_candidates == 0:
            return None

        if total_candidates == 1:
            entity_slots = []
            for entity in candidate_entity_slots[0]:
                entity_slots.append((entity,))
            return entity_slots

        if use_all_combinations:
            candidate_entity_slots = candidate_entity_slots[:slot_limit]

            entity_slots = itertools.product(candidate_entity_slots[0], candidate_entity_slots[1])
            for idx in range(2, len(candidate_entity_slots)):
                entity_slots = itertools.product(entity_slots, candidate_entity_slots[idx])
                all_entity_slots = []
                for already_merged_entity_slots, unmerged_entity_slot in entity_slots:
                    merged_entity_slots = ()
                    for already_merged_entity_slot in already_merged_entity_slots:
                        merged_entity_slots += (already_merged_entity_slot,)
                    merged_entity_slots += (unmerged_entity_slot,)
                    all_entity_slots.append(merged_entity_slots)
                entity_slots = all_entity_slots
            return entity_slots

        else:
            entity_slots = []
            for version in range(total_versions):
                entity_slot = ()
                for candidate_entity_slot in candidate_entity_slots:
                    slot_value = np.random.choice(candidate_entity_slot)
                    entity_slot += (slot_value,)
                entity_slots.append(entity_slot)
            return entity_slots

    def get_slot_replaced_utterances(self, utterances, use_all_combinations=False, slot_limit=4, total_versions=10):
        for utt_idx, utterance in enumerate(utterances):
            if utt_idx == 0:
                yield utterance.text
                if len(utterances) > 1:
                    continue

            entity_slots = self.get_all_entity_slot_combinations(utterance=utterance, \
                                                                 use_all_combinations=use_all_combinations,
                                                                 slot_limit=slot_limit, total_versions=total_versions)

            if entity_slots is not None:
                for entity_slot in entity_slots:
                    idx = 0
                    slot_replaced_utterance = []
                    for token in utterance:
                        if token._.entity_value is None:
                            slot_replaced_utterance.append(token.text)
                        else:
                            if idx < slot_limit:
                                slot_replaced_utterance.append(entity_slot[idx])
                                idx += 1
                            else:
                                slot_replaced_utterance.append(token.text)
                    yield ' '.join(slot_replaced_utterance)
            else:
                yield utterance.text
