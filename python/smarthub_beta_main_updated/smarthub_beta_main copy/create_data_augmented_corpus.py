import os
os.environ['CUDA_VISIBLE_DEVICES'] = '0'
os.environ["OMP_NUM_THREADS"] = '4'
os.environ["OPENBLAS_NUM_THREADS"] = '5'
os.environ["MKL_NUM_THREADS"] = '6'
os.environ["VECLIB_MAXIMUM_THREADS"] = '4'
os.environ["NUMEXPR_NUM_THREADS"] = '6'
os.environ["NUMEXPR_NUM_THREADS"] = '5'

import json

from dev.corpus_data_augmentor.paraphraser import Paraphraser
from dev.corpus_data_augmentor.parser import Parser
from dev.corpus_data_augmentor.slot_replacer import SlotReplacer
from dev.corpus_data_augmentor.synonym_replacer import SynonymReplacer
from dev.corpus_data_augmentor.utils import Utils
from dev.corpus_extractor.corpus_extraction_paths import CorpusExtractionPaths
from dev.corpus_feature_extractor.corpus_feature_extractor_utils import CorpusFeatureExtractorUtils
from model_paths import ModelPaths
from dev.corpus_data_augmentor.data_augmentor_paths import DataAugmentorPaths

augment_with_paraphrases = True
augment_with_slot_replacement = True
augment_with_synonym_replacement = False
total_versions = 10

corpus_path = Utils.get_corpus_path(
    augment_with_paraphrases=augment_with_paraphrases,
    augment_with_slot_replacement=augment_with_slot_replacement,
    augment_with_synonym_replacement=augment_with_synonym_replacement,
    total_versions=total_versions)

print("Writing data augmented corpus to", corpus_path)
subject_context = dict()

corpus_entity_extractor = CorpusFeatureExtractorUtils.get_context_based_corpus_entity_extractor()

paraphraser = None
if augment_with_paraphrases:
    paraphraser = Paraphraser(paraphrases_json_path=DataAugmentorPaths.PARAPHRASES_DIR)

slot_replacer = None
if augment_with_slot_replacement:
    slot_replacer = SlotReplacer(corpus_entity_extractor=corpus_entity_extractor)

synonym_replacer = None
if augment_with_synonym_replacement:
    synonym_replacer = SynonymReplacer(use_index=False, use_wordnet=True,
                                       corpus_entity_extractor=corpus_entity_extractor)

subject_context_versions = Parser.parse(
    corpus_path=CorpusExtractionPaths.JSON_CORPUS_DATA,
    corpus_entity_extractor=corpus_entity_extractor,
    paraphraser=paraphraser,
    slot_replacer=slot_replacer,
    synonym_replacer=synonym_replacer,
    total_versions=total_versions,
    process_refexps=False)

with open(corpus_path, 'a+') as f:
    f.write('[')
    f.write('\n')

for subject_context_version in subject_context_versions:
    subject_context['subject_name'] = subject_context_version['subject_name']
    subject_context['contexts'] = []

    for version_id in range(total_versions):
        subject_context_cpy = dict(subject_context)
        subject_context_cpy['subject_name'] += '_' + str(version_id)
        subject_context_cpy['contexts'].clear()

        print("Processing subject", subject_context_cpy['subject_name'],
              "Version", version_id)

        for context_versions in subject_context_version['contexts']:
            subject_context_cpy['contexts'].append(
                context_versions.get_context_components_version(
                    version_id))

        print("Writing Subject", subject_context['subject_name'], "Version", version_id,
              "with Total Contexts", len(subject_context_version['contexts']))
        with open(corpus_path, 'a+') as f:
            json.dump(obj=subject_context_cpy, indent=4, fp=f)
            f.write(',')
            f.write('\n')
        print("Completed writing subject", subject_context['subject_name'],
              "Version", version_id)

with open(corpus_path, 'a+') as f:
    f.write(']')
    f.write('\n')
