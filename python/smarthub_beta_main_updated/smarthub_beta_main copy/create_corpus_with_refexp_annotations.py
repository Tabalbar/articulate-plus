import dev.text_segmentation_model as inc
from dev.corpus_extractor.corpus_extraction_paths import CorpusExtractionPaths
from dev.corpus_extractor.extractor import Extractor
from dev.corpus_extractor.utterance_processing_utils import UtteranceProcessingUtils
from dev.corpus_feature_extractor.corpus_feature_extractor_utils import CorpusFeatureExtractorUtils
from dev.text_tokenizer_pipeline.text_processing_utils import TextProcessingUtils

annotated_utterances_by_subject = dict(
    Extractor.extract(corpus_path=CorpusExtractionPaths.JSON_CORPUS_DATA, process_refexps=True))

annotation_mapping = dict()
for subject, context_components in annotated_utterances_by_subject.items():
    if subject not in annotation_mapping:
        annotation_mapping[subject] = dict()
    for contexts in context_components:
        for context in contexts.get_context():
            if type(context) != list:
                utterance_id = context.get_utterance().get_utteranceid_attribute()
                annotation_mapping[subject][utterance_id] = dict()
                annotation_mapping[subject][utterance_id]['context'] = context
                annotation_mapping[subject][utterance_id]['referringexpression'] = None
            else:
                for utterance in context:
                    utterance_id = utterance.get_utterance().get_utteranceid_attribute()
                    annotation_mapping[subject][utterance_id] = dict()
                    annotation_mapping[subject][utterance_id]['context'] = utterance
                    annotation_mapping[subject][utterance_id]['referringexpression'] = None


class Constants:
    GESTURE = 'Gesture'
    TEXT = 'Text'
    EST = 'Est'
    ALL = [GESTURE, TEXT, EST]


def update_ranges(refexp_ranges, target):
    for idx in range(len(refexp_ranges)):
        refexp_range = refexp_ranges[idx]
        if refexp_range[0] >= target:
            refexp_range[0] += 1
        if refexp_range[1] >= target:
            refexp_range[1] += 1
    return refexp_ranges


def insert_bracket_boundaries(utterance, multimodal_referringexpressions, referringexpression_type):
    refexp_ranges = []
    referringexpression_id = None
    for referringexpressions in multimodal_referringexpressions:
        exists = False
        for i, referringexpression in enumerate(referringexpressions.get_referringexpression_attribute()):
            print("REFID", referringexpression.rid, \
                  "TYPE", referringexpression_type, "TESTREF", \
                  referringexpression, "I", i, "START", referringexpression.get_start_word_idx(), \
                  "END", referringexpression.get_end_word_idx())
            refexp_ranges.append(([referringexpression.get_start_word_idx(), referringexpression.get_end_word_idx()], \
                                  referringexpression.rid, \
                                  referringexpression.targets))

    [r[0] for r in refexp_ranges].sort(key=lambda x: x[0])

    tokens = utterance.split()

    for idx in range(len(refexp_ranges)):
        refexp_range, referringexpression_id, referringexpression_targets = refexp_ranges[idx]
        start = refexp_range[0]
        tokens.insert(start, '[' + referringexpression_type + '<' + str(referringexpression_id) + '><' + \
                      referringexpression_targets.replace(' ', '') + '>:')
        update_ranges(refexp_ranges=[r[0] for r in refexp_ranges], target=start)

    for idx in range(len(refexp_ranges)):
        refexp_range, referringexpression_id, referringexpression_targets = refexp_ranges[idx]
        end = refexp_range[1]
        if end - 1 < len(tokens) and '[' in tokens[end - 1]:
            tokens.insert(end - 1, referringexpression_type + '<' + str(referringexpression_id) + '><' + \
                          referringexpression_targets.replace(' ', '') + '>]')
        else:
            tokens.insert(end, referringexpression_type + '<' + str(referringexpression_id) + '><' + \
                          referringexpression_targets.replace(' ', '') + '>]')
        update_ranges(refexp_ranges=[r[0] for r in refexp_ranges], target=end)
    return ' '.join(tokens)


def merge(str1, str2):
    if not str1:
        return str2

    if not str2:
        return str1

    str_arr1 = str1.split()
    str_arr2 = str2.split()
    i, j = 0, 0

    while i < len(str_arr1) and j < len(str_arr2):
        if str_arr1[i] == str_arr2[j]:
            i += 1
            j += 1

        elif [val for val in Constants.ALL if val in str_arr2[j]]:
            if '[' in str_arr1[i]:
                str_arr1.insert(i, str_arr2[j])
                i += 2
                j += 1

            elif ']' in str_arr1[i]:
                str_arr1.insert(i + 1, str_arr2[j])
                i += 2
                j += 1
            else:
                str_arr1.insert(i, str_arr2[j])

        elif [val for val in Constants.ALL if val in str_arr1[i]]:
            if '[' in str_arr2[j]:
                str_arr2.insert(j, str_arr1[i])
                j += 2
                i += 1
            elif ']' in str_arr2[j]:
                str_arr2.insert(j + 1, str_arr1[i])
                j += 2
                i += 1
            else:
                str_arr2.insert(j, str_arr1[i])
    if str_arr1[-1] == str_arr2[-1]:
        return ' '.join(str_arr1)

    if ']' in str_arr1[-1]:
        str_arr2.append(str_arr1[-1])
    elif ']' in str_arr2[-1]:
        str_arr1.append(str_arr2[-1])

    return ' '.join(str_arr1)


def merge_all(bracketed_gestures, bracketed_texts, bracketed_vis):
    print("Gest", bracketed_gestures)
    print("Text", bracketed_texts)
    print("Est", bracketed_vis)

    current_str = merge(bracketed_gestures, bracketed_texts)
    current_str = merge(current_str, bracketed_vis)

    print("merged", current_str)
    return current_str


nlp = CorpusFeatureExtractorUtils.get_context_based_corpus_entity_extractor().get_tokenizer()

for sbj in range(5, 21):
    subject = 'subject' + str(sbj)
    print("CURRENT SUBJECT", subject)

    for uttid, data in annotation_mapping[subject].items():
        uttid = data['context'].get_utterance().get_utteranceid_attribute()
        utt = data['context'].get_utterance().get_utterance_attribute()

        print('\n\nPROCESSING', uttid, utt)
        utt = UtteranceProcessingUtils.clean_utterance(
            TextProcessingUtils.clean_text(text=utt),
            remove_hyphens=True)
        doc = nlp(utt)

        norm = []
        for t in doc:
            norm.append('-'.join(t.text.split()))

        nps = []

        freq = {}
        for idx, d in enumerate(doc):
            if d.text not in freq:
                freq[d.text] = []
            freq[d.text].append((idx))

        for d in doc.noun_chunks:
            is_pron = False
            for t in d:
                if t.pos_ == 'PRON':
                    is_pron = True
            if is_pron:
                continue

            for t in d:
                if len(freq[t.text]) > 1:
                    print(t.text + " occurred " + str(freq[t.text]) + ' times\n')

            nps.append(d.text + '@@@1')

        print("NOUN PHRASES", ';'.join(nps))

        bracketed_gestures, bracketed_texts, bracketed_vis = None, None, None
        gesture_referringexpression_id, text_referringexpression_id, vis_referringexpression_id = None, None, None
        gesture_targets, text_targets, vis_targets = None, None, None
        if data['context'].get_gesture_based_referring_expression():
            bracketed_gestures = insert_bracket_boundaries(utterance=utt,
                                                           multimodal_referringexpressions=
                                                           data['context'].get_gesture_based_referring_expression(),
                                                           referringexpression_type=Constants.GESTURE)

        if data['context'].get_text_based_referring_expression():
            bracketed_texts = insert_bracket_boundaries(utterance=utt,
                                                        multimodal_referringexpressions=
                                                        data['context'].get_text_based_referring_expression(),
                                                        referringexpression_type=Constants.TEXT)

        if data['context'].get_visualization_reference():
            bracketed_vis = insert_bracket_boundaries(utterance=utt,
                                                      multimodal_referringexpressions=
                                                      data['context'].get_visualization_reference(),
                                                      referringexpression_type=Constants.EST)

        bracketed = merge_all(bracketed_gestures, bracketed_texts, bracketed_vis)
        annotation_mapping[subject][uttid]['referringexpression'] = bracketed
        print("\n\n")

cseg = inc.gold_text_segmenter.GoldTextSegmenter()
corpus_segments_by_subject = cseg.get_segments_by_subject()
utterances_by_subject = cseg.get_utterances_by_subject()

corpus_path = CorpusExtractionPaths.REFERRING_EXPRESSION_EXTRACTION_DATA_PATH
for sbj in range(5, 21):
    subject = 'subject' + str(sbj)
    print("writing annotated text for subject", subject)
    tagged_text = subject + '\n\n'
    annotated_text = ''
    for line_id, utterance_id, utterance, ar, utterance_obj in utterances_by_subject[subject]:
        if utterance_id == -1:
            print(utterance)
            tagged_text += utterance + '\n'
        else:
            data = annotation_mapping[subject][str(utterance_id)]
            if data['referringexpression'] is None:
                print(data['context'].get_utterance().get_utterance_attribute())
                tagged_text += data['context'].get_utterance().get_utterance_attribute() + '\n'
            else:
                print(data['referringexpression'])
                tagged_text += data['referringexpression'] + '\n'

                refexp = data['referringexpression']
                lst = set()
                for word in refexp.split():
                    if [val for val in Constants.ALL if val in word]:
                        if '[' in word:
                            tokens = word[1:].split('<')
                            lst.add(tokens[0] + '\t' + \
                                    tokens[1][:-1] + '\t' + \
                                    tokens[2][:-2] + '\n')
                        else:
                            tokens = word[:-1].split('<')
                            lst.add(tokens[0] + '\t' + \
                                    tokens[1][:-1] + '\t' + \
                                    tokens[2][:-1] + '\n')
                annotated_text += ''.join(lst)

        with open(corpus_path + subject + '.txt', 'w') as f:
            f.write(tagged_text)
        with open(corpus_path + subject + '_referringexpressions.txt', 'w') as f:
            f.write(annotated_text)
