import os
os.environ['CUDA_VISIBLE_DEVICES'] = '0'
os.environ["OMP_NUM_THREADS"] = '4'
os.environ["OPENBLAS_NUM_THREADS"] = '5'
os.environ["MKL_NUM_THREADS"] = '6'
os.environ["VECLIB_MAXIMUM_THREADS"] = '4'
os.environ["NUMEXPR_NUM_THREADS"] = '6'
os.environ["NUMEXPR_NUM_THREADS"] = '5'

from dev.corpus_data_augmentor.utils import Utils
from dev.corpus_extractor.corpusannotations.referring_expression_info import ReferringExpressionInfo
from dev.corpus_extractor.corpus_extraction_paths import CorpusExtractionPaths
from dev.corpus_extractor.extractor import Extractor
from dev.corpus_feature_extractor.corpus_feature_extractor_utils import CorpusFeatureExtractorUtils


augment_with_paraphrases = True
augment_with_slot_replacement = True
augment_with_synonym_replacement = False
total_versions = 10

corpus_path = Utils.get_corpus_path(
    augment_with_paraphrases=augment_with_paraphrases,
    augment_with_slot_replacement=augment_with_slot_replacement,
    augment_with_synonym_replacement=augment_with_synonym_replacement,
    total_versions=total_versions)

outputfilepath_by_subject = dict()
annotated_utterances_by_subject_with_processed_refexps = \
    dict(Extractor.extract_from_json(corpus_path=corpus_path, process_refexps=True))
annotated_utterances_by_subject_with_unprocessed_refexps = \
    dict(Extractor.extract_from_json(corpus_path=corpus_path, process_refexps=False))

annotated_utterances_by_version_id = {}
for version_id in range(0, 10):
    annotated_utterances_by_version_id[version_id] = []
    for sbj in range(5, 21):
        subject = 'subject' + str(sbj) + '_' + str(version_id)
        if version_id == 0:
            annotated_utterances_by_version_id[version_id].append(( \
                subject, annotated_utterances_by_subject_with_processed_refexps[subject]))
        else:
            annotated_utterances_by_version_id[version_id].append(( \
                subject, annotated_utterances_by_subject_with_unprocessed_refexps[subject]))
        outputfilepath_by_subject[subject] = CorpusExtractionPaths.REFERRING_EXPRESSION_EXTRACTION_AND_NAMED_ENTITIES_DATA_PATH + \
                                             'subject' + str(sbj) + '_' + str(version_id) + '.csv'

for subject in set(outputfilepath_by_subject.values()):
    with open(subject, 'a+') as f:
        f.write('Sentence #,Word,POS,NER_Tag,RefExp_Tag\n')


def does_range_already_exists(start, end, ranges):
    for r in ranges:
        if start >= r[0] and end <= r[1]:
            return True
    return False


def insert_referringexpression_to_range(referringexpressions, ranges):
    if not referringexpressions:
        return

    for refs in referringexpressions:
        for ref in refs.get_referringexpression_attribute():
            if not isinstance(ref, ReferringExpressionInfo):
                continue

            start = ref.get_start_word_idx()
            end = ref.get_end_word_idx()
            if not does_range_already_exists(start, end, ranges):
                ranges.append((start, end))


def is_in_range(word_idx, ranges):
    for r in ranges:
        if r[0] <= word_idx < r[1]:
            return True
    return False


nlp = CorpusFeatureExtractorUtils.get_context_based_corpus_entity_extractor() \
    .get_tokenizer()
annotation_mapping = dict()
sentence_id = 0
for version_id in annotated_utterances_by_version_id.keys():
    if version_id not in annotation_mapping:
        print("***Processing version***", version_id)
        annotation_mapping[version_id] = dict()
    for subject, context_components in annotated_utterances_by_version_id[version_id]:
        output_file = open(outputfilepath_by_subject[subject], 'a+')
        print("******Processing subject******", subject)
        if subject not in annotation_mapping[version_id]:
            annotation_mapping[version_id][subject] = dict()
        for contexts in context_components:
            for context in contexts.get_context():
                if type(context) != list:
                    utterance_id = context.get_utterance().get_utteranceid_attribute()
                    utterance = context.get_utterance().get_utterance_attribute()
                    print("utterance", utterance)

                    referring_expression_ranges = []
                    gestref = context.get_gesture_based_referring_expression()
                    insert_referringexpression_to_range(gestref, referring_expression_ranges)

                    textref = context.get_text_based_referring_expression()
                    insert_referringexpression_to_range(textref, referring_expression_ranges)

                    output = 'Sentence: ' + str(sentence_id)
                    prev_refexp_label = 'O'
                    curr_refexp_label = prev_refexp_label
                    word_idx = 0
                    print(subject, output, utterance)
                    if len(utterance.split()) < 4:
                        continue
                    for phrase in nlp(utterance):
                        phrase_text, ner_label, pos, tag, dep, start_char, end_char = \
                            (phrase.text, phrase._.entity, \
                             phrase.pos_, phrase.tag_, phrase.dep_, \
                             phrase._.start_char, phrase._.end_char)

                        if not ner_label and len(phrase_text.split()) == 1:
                            ner_label = 'O'
                        elif not ner_label:
                            ner_label = 'B-unk'
                        else:
                            ner_label = 'B-' + ner_label
                        for word in phrase_text.split():
                            if is_in_range(word_idx, referring_expression_ranges) and \
                                    prev_refexp_label == 'O':
                                curr_refexp_label = 'B-ref'
                            elif is_in_range(word_idx, referring_expression_ranges):
                                curr_refexp_label = 'I-ref'
                            else:
                                curr_refexp_label = 'O'

                            prev_refexp_label = curr_refexp_label

                            if word == ',':
                                output += ',' + '' + ',' + pos + ',' + ner_label + ',' + curr_refexp_label + '\n'
                            elif ',' in word:
                                s = word.replace(',', '')
                                output += ',' + s + ',' + pos + ',' + ner_label + ',' + curr_refexp_label + '\n'
                            else:
                                output += ',' + word + ',' + pos + ',' + ner_label + ',' + curr_refexp_label + '\n'
                            ner_label = 'I-' + ner_label[2:]
                            word_idx += 1

                    annotation_mapping[version_id][subject][utterance_id] = dict()
                    annotation_mapping[version_id][subject][utterance_id][
                        'context'] = context.get_context_component_as_json()
                    annotation_mapping[version_id][subject][utterance_id]['entities'] = output
                    output_file.write(output)
                    sentence_id += 1
                else:
                    for utterance_obj in context:
                        utterance_id = utterance_obj.get_utterance().get_utteranceid_attribute()
                        utterance = utterance_obj.get_utterance().get_utterance_attribute()
                        print("utterance", utterance)

                        referring_expression_ranges = []
                        gestref = utterance_obj.get_gesture_based_referring_expression()
                        insert_referringexpression_to_range(gestref, referring_expression_ranges)

                        textref = utterance_obj.get_text_based_referring_expression()
                        insert_referringexpression_to_range(textref, referring_expression_ranges)

                        output = 'Sentence: ' + str(sentence_id)
                        prev_refexp_label = 'O'
                        curr_refexp_label = prev_refexp_label
                        word_idx = 0
                        print(subject, output, utterance)
                        if len(utterance.split()) < 4:
                            continue
                        for phrase in nlp(utterance):
                            phrase_text, ner_label, pos, tag, dep, start_char, end_char = \
                                (phrase.text, phrase._.entity,
                                 phrase.pos_, phrase.tag_, phrase.dep_,
                                 phrase._.start_char, phrase._.end_char)

                            if not ner_label and len(phrase_text.split()) == 1:
                                ner_label = 'O'
                            elif not ner_label:
                                ner_label = 'B-unk'
                            else:
                                ner_label = 'B-' + ner_label
                            for word in phrase_text.split():
                                if is_in_range(word_idx, referring_expression_ranges) and \
                                        prev_refexp_label == 'O':
                                    curr_refexp_label = 'B-ref'
                                elif is_in_range(word_idx, referring_expression_ranges):
                                    curr_refexp_label = 'I-ref'
                                else:
                                    curr_refexp_label = 'O'

                                prev_refexp_label = curr_refexp_label

                                if word == ',':
                                    output += ',' + '' + ',' + pos + ',' + ner_label + ',' + curr_refexp_label + '\n'
                                elif ',' in word:
                                    s = word.replace(',', '')
                                    output += ',' + s + ',' + pos + ',' + ner_label + ',' + curr_refexp_label + '\n'
                                else:
                                    output += ',' + word + ',' + pos + ',' + ner_label + ',' + curr_refexp_label + '\n'
                                ner_label = 'I-' + ner_label[2:]
                                word_idx += 1

                        annotation_mapping[version_id][subject][utterance_id] = dict()
                        annotation_mapping[version_id][subject][utterance_id][
                            'context'] = utterance_obj.get_context_component_as_json()
                        annotation_mapping[version_id][subject][utterance_id]['entities'] = output
                        output_file.write(output)
                        sentence_id += 1
        output_file.close()

import json

with open('full_corpus_annotations.json', 'w') as f:
    f.write(json.dumps(annotation_mapping, default=lambda o: o.__dict__, indent=4))
