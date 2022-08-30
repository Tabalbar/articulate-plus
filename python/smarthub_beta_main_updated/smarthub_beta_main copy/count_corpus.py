from dev.corpus_extractor.corpus_extraction_paths import CorpusExtractionPaths
from dev.corpus_extractor.extractor import Extractor

counts = dict()
counts['prev'] = 0
counts['current'] = 0
counts['next'] = 0

counts['setup'] = 0
counts['request'] = 0
counts['conclusion'] = 0

counts['utterances'] = 0
counts['referringexpressions'] = 0
counts['gestures'] = 0
counts['visualizationreferences'] = 0

counts['prev_utterances'] = 0
counts['prev_referringexpressions'] = 0
counts['prev_gestures'] = 0
counts['prev_gesturereferences'] = 0
counts['prev_visualizationreferences'] = 0

counts['setup_utterances'] = 0
counts['setup_referringexpressions'] = 0
counts['setup_gestures'] = 0
counts['setup_gesturereferences'] = 0
counts['setup_visualizationreferences'] = 0

counts['current_utterances'] = 0
counts['current_referringexpressions'] = 0
counts['current_gestures'] = 0
counts['current_gesturereferences'] = 0
counts['current_visualizationreferences'] = 0

counts['request_type'] = dict()
counts['request_utterances'] = 0
counts['request_referringexpressions'] = 0
counts['request_gestures'] = 0
counts['request_gesturereferences'] = 0
counts['request_visualizationreferences'] = 0

counts['next_utterances'] = 0
counts['next_referringexpressions'] = 0
counts['next_gestures'] = 0
counts['next_gesturereferences'] = 0
counts['next_visualizationreferences'] = 0

counts['conclusion_utterances'] = 0
counts['conclusion_referringexpressions'] = 0
counts['conclusion_gestures'] = 0
counts['conclusion_gesturereferences'] = 0
counts['conclusion_visualizationreferences'] = 0

data = Extractor.extract(corpus_path=CorpusExtractionPaths.JSON_CORPUS_DATA, utterance_cutoff=-1, process_refexps=False)
refexpfreq = []
for subject in data:
    subject_name = subject[0]
    contexts = subject[1]
    for context in contexts:
        setup = context.get_setup()
        request = context.get_request()
        conclusion = context.get_conclusion()

        counts['prev'] += len(setup)
        counts['current'] += 1
        counts['next'] += len(conclusion)

        already_added = [False, False, False, False, False]
        for p in setup:
            utterance, gesture, gesture_refexp, text_refexp, vis_ref = p.get_context_component()

            if utterance is not None:
                counts['utterances'] += 1
                counts['prev_utterances'] += 1

                if not already_added[0]:
                    counts['setup_utterances'] += 1
                    already_added[0] = True

            if gesture is not None:
                counts['gestures'] += len(gesture)
                counts['prev_gestures'] += len(gesture)

                if not already_added[1]:
                    counts['setup_gestures'] += 1
                    already_added[1] = True

            if gesture_refexp is not None:
                counts['referringexpressions'] += len(gesture_refexp)
                counts['prev_referringexpressions'] += len(gesture_refexp)
                counts['prev_gesturereferences'] += len(gesture_refexp)

                if not already_added[2]:
                    counts['setup_referringexpressions'] += 1
                    counts['setup_gesturereferences'] += 1
                    already_added[2] = True

            if text_refexp is not None:
                refexpfreq.append(text_refexp[0].get_referringexpression_attribute())
                counts['referringexpressions'] += len(text_refexp)
                counts['prev_referringexpressions'] += len(text_refexp)

                if not already_added[3]:
                    counts['setup_referringexpressions'] += 1
                    already_added[3] = True

            if vis_ref is not None:
                for ref in vis_ref:
                    refexp = ref.get_referringexpression_attribute()
                    targetids = ref.get_targetvis_ids_attribute().split()
                    sourceids = ref.get_sourcevis_ids_attribute().split()

                    refexpfreq.append(refexp)

                    if sourceids is not None:
                        continue

                    if targetids is None:
                        continue

                    if refexp == None:
                        continue
                    counts['referringexpressions'] += 1
                    counts['prev_referringexpressions'] += 1

                    if not already_added[4]:
                        counts['setup_referringexpressions'] += 1

                counts['visualizationreferences'] += len(vis_ref)
                counts['prev_visualizationreferences'] += len(vis_ref)

                if not already_added[4]:
                    counts['setup_visualizationreferences'] += 1
                    already_added[4] = True

        already_added = [False, False, False, False]
        utterance, gesture, gesture_refexp, text_refexp, vis_ref = request.get_context_component()

        if utterance is not None:
            counts['utterances'] += 1
            counts['current_utterances'] += 1
            counts['request_utterances'] += 1

            utttype = utterance.get_utterancetype_attribute()
            if utttype not in counts['request_type']:
                counts['request_type'][utttype] = 0
            counts['request_type'][utttype] += 1
            already_added[0] = True

        if gesture is not None:
            counts['gestures'] += len(gesture)
            counts['current_gestures'] += len(gesture)
            counts['request_gestures'] += 1
            already_added[1] = True

        if gesture_refexp is not None:
            counts['referringexpressions'] += len(gesture_refexp)
            counts['current_referringexpressions'] += len(gesture_refexp)
            counts['current_gesturereferences'] += len(gesture_refexp)
            if not already_added[2]:
                counts['request_referringexpressions'] += 1
                counts['request_gesturereferences'] += 1
                already_added[2] = True

        if text_refexp is not None:
            refexpfreq.append(text_refexp[0].get_referringexpression_attribute())

            counts['referringexpressions'] += len(text_refexp)
            counts['current_referringexpressions'] += len(text_refexp)
            if not already_added[2]:
                counts['request_referringexpressions'] += 1
                already_added[2] = True

        if vis_ref is not None:
            for ref in vis_ref:
                refexp = ref.get_referringexpression_attribute()
                targetids = ref.get_targetvis_ids_attribute().split()
                sourceids = ref.get_sourcevis_ids_attribute().split()

                if sourceids is not None:
                    continue

                if targetids is None:
                    continue

                if refexp == None:
                    continue
                counts['referringexpressions'] += 1
                counts['current_referringexpressions'] += 1

                if not already_added[3]:
                    counts['request_referringexpressions'] += 1

            counts['visualizationreferences'] += len(vis_ref)
            counts['current_visualizationreferences'] += len(vis_ref)
            if not already_added[3]:
                counts['request_visualizationreferences'] += 1
                already_added[3] = True

        already_added = [False, False, False, False, False]
        for p in conclusion:
            utterance, gesture, gesture_refexp, text_refexp, vis_ref = p.get_context_component()

            if utterance is not None:
                counts['utterances'] += 1
                counts['next_utterances'] += 1

                if not already_added[0]:
                    counts['conclusion_utterances'] += 1
                    already_added[0] = True

            if gesture is not None:
                counts['gestures'] += len(gesture)
                counts['next_gestures'] += len(gesture)

                if not already_added[1]:
                    counts['conclusion_gestures'] += 1
                    already_added[1] = True

            if gesture_refexp is not None:
                counts['referringexpressions'] += len(gesture_refexp)
                counts['next_referringexpressions'] += len(gesture_refexp)
                counts['next_gesturereferences'] += len(gesture_refexp)

                if not already_added[2]:
                    counts['conclusion_gesturereferences'] += 1
                    counts['conclusion_referringexpressions'] += 1
                    already_added[2] = True

            if text_refexp is not None:
                refexpfreq.append(text_refexp[0].get_referringexpression_attribute())
                counts['referringexpressions'] += len(text_refexp)
                counts['next_referringexpressions'] += len(text_refexp)

                if not already_added[3]:
                    counts['conclusion_referringexpressions'] += 1
                    already_added[3] = True

            if vis_ref is not None:
                for ref in vis_ref:
                    refexp = ref.get_referringexpression_attribute()
                    targetids = ref.get_targetvis_ids_attribute().split()
                    sourceids = ref.get_sourcevis_ids_attribute().split()

                    if sourceids is not None:
                        continue

                    if targetids is None:
                        continue

                    if refexp == None:
                        continue
                    counts['referringexpressions'] += 1
                    counts['next_referringexpressions'] += 1

                    if not already_added[4]:
                        counts['conclusion_referringexpressions'] += 1

                counts['visualizationreferences'] += len(vis_ref)
                counts['next_visualizationreferences'] += len(vis_ref)
                if not already_added[4]:
                    counts['conclusion_visualizationreferences'] += 1
                    already_added[4] = True

        if len(setup) > 0:
            counts['setup'] += 1

        if request is not None:
            counts['request'] += 1

        if len(conclusion) > 0:
            counts['conclusion'] += 1

for stat_name, stat_count in sorted(counts.items()):
    print(stat_name, stat_count)

refexp_data = []
for refexps in refexpfreq:
    for token in refexps.split(';'):
        refexp = token.split('@@@')[0]
        if refexp == 'none':
            continue
        if '[' in refexp:
            refexp_data.append(refexp[1:])
        elif ']' in refexp:
            refexp_data.append(refexp[:-1])
        elif '[' in refexp and ']' in refexp:
            refexp_data.append(refexp[1:-1])
        else:
            refexp_data.append(refexp)
