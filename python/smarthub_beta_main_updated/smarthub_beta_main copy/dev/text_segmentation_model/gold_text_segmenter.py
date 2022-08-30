from .segmenter import Segmenter
from ..corpus_extractor.corpus_extraction_paths import CorpusExtractionPaths
from ..corpus_extractor.extractor import Extractor
from ..corpus_extractor.transcript_extractor import TranscriptExtractor


class GoldTextSegmenter(Segmenter):
    def __init__(self):
        super().__init__()

    def get_segments_by_subject(self, unseen_subjects, fold=0):
        if self._segments_by_subject:
            return self._segments_by_subject

        # annotated corpus
        annotated_utterances_by_subject = dict(
            Extractor.extract(corpus_path=CorpusExtractionPaths.JSON_CORPUS_DATA))

        # transcripts (by subject)
        transcripted_utterances_by_subject = TranscriptExtractor().get_transcripts \
            (path=CorpusExtractionPaths.TRANSCRIPT_CORPUS_DATA_PATH)

        # iterate through the 16 subjects
        for subject in ['subject' + str(i) for i in range(5, 21)]:
            print("SUBJECT", subject)

            transcript_utterances = [(line_id, utterance.text, utterance) for line_id, utterance in
                                        enumerate(transcripted_utterances_by_subject[subject])
                                            if len(utterance.text.split()) > 3]
            print("Total transcripted utterances", len(transcript_utterances), "for subject", subject)

            # get all annotated utterances for current subject
            annotated_utterances = []

            # Identify each utterance id as setup, request, or conclusion
            car = {}
            for context in annotated_utterances_by_subject[subject]:
                for setup_utterance in context.get_setup():
                    utterance = self._clean_utterance(setup_utterance.get_utterance().get_utterance_attribute())
                    utterance_id = int(setup_utterance.get_utterance().get_utteranceid_attribute())
                    annotated_utterances.append((utterance_id, utterance))
                    car[utterance_id] = 'setup'

                utterance = self._clean_utterance(context.get_request().get_utterance().get_utterance_attribute())
                utterance_id = int(context.get_request().get_utterance().get_utteranceid_attribute())
                annotated_utterances.append((utterance_id, utterance))
                car[utterance_id] = 'request'

                for conclusion_utterance in context.get_conclusion():
                    utterance = self._clean_utterance(conclusion_utterance.get_utterance().get_utterance_attribute())
                    utterance_id = int(conclusion_utterance.get_utterance().get_utteranceid_attribute())
                    annotated_utterances.append((utterance_id, utterance))
                    car[utterance_id] = 'conclusion'
            print("Total annotated utterances", len(annotated_utterances), "for subject", subject)

            # In order to match transcripts to annotations, sort by longer utterances first,
            # so that false matches do not occur on smaller ones. These are sorted in descending order
            # according to the utterance id.
            transcript_utterances.sort(key=lambda x: len(x[1]), reverse=True)
            annotated_utterances.sort(key=lambda x: len(x[1]), reverse=True)

            # All matches are contained here, as (line_id,utterance_id,utterance,ar,utterance_obj) tuple.
            # Line id is the line number in the transcript (integer)
            # Utterance id is the utterance id given in the annotations (integer)
            # ar is the annotated utterance (string)
            # utterace_obj is the transcript utterance (Spacy object).
            #	i.e., utterance_obj.text gives you the string form and utterance_obj._.entities
            #	gives you the named entities contained in the transcript utterance
            matches = []

            # In certain cases, there can be more than 1 match and we keep these in here.
            # This occurs because a substring from the transcript matches to more than one annotated utterance.
            # Later on, we will process to select the correct match.
            alternatives = dict()

            # Iterate through each transcripted utterance and find a corresponding match in the annotation utterances.
            for line_id, utterance, utterance_obj in transcript_utterances:
                is_found = False
                for utterance_id, ar in annotated_utterances:
                    if utterance.strip() in ar.strip() and utterance_id <= line_id and utterance_id:
                        # This is the first time there is a match with this particular transcript utterance and annotated one.
                        if not is_found:
                            matches.append((line_id, utterance_id, utterance, ar, utterance_obj))
                            is_found = True

                        # Another match is found with this particular transcript utterance so store as possible alternatives.
                        else:
                            if not line_id in alternatives:
                                alternatives[line_id] = []
                            alternatives[line_id].append((line_id, utterance_id, utterance, ar, utterance_obj))

                # Never found a match so this is a transcripted utterance that is not been annotated.
                if not is_found:
                    matches.append((line_id, -1, utterance, '', utterance_obj))

            # Sort the matches in ascending order according to the Line id
            matches.sort(key=lambda x: x[0])

            # Every subsequent utterance id should be larger than the previous one in the matches.
            # Otherwise, something is wrong since in our annotations, utterance ids are in increasing order.
            # When that happens, we need to identify the valid ranges and then choose from the alternative the one
            # that is within the valid range of utterance ids.
            curr_utt_id = matches[0][1]
            prev_utt_id = curr_utt_id

            for i in range(len(matches)):
                curr_utt_id = matches[i][1]
                if curr_utt_id == -1:
                    continue

                # Previous utterance id is larger so there is some wrong utterance.
                if prev_utt_id > curr_utt_id:
                    # select the from_r (range) and to_r (range) that are valid utterance ids.
                    # Choose any alternative that is within the valid range (or choose none if there are no valid ones).
                    from_r = i - 1
                    while from_r >= 0 and matches[from_r][1] == -1:
                        from_r -= 1

                    if from_r < 0:
                        from_r = 0

                    to_r = i + 1
                    while to_r < len(matches) and matches[to_r][1] == -1:
                        to_r += 1

                    if to_r >= len(matches):
                        to_r = len(matches) - 1

                    if matches[from_r][1] == -1:
                        target_idx = i - 1
                        target = matches[target_idx]

                        r = (matches[to_r][1], matches[to_r][1])

                        if target[0] in alternatives and r[0] < alternatives[target[0]][0][1] < r[1]:
                            # print("update",target,"with valid range",r,"VAL",alternatives[target[0]][0])
                            matches[target_idx] = alternatives[target[0]][0]
                        else:
                            matches[target_idx] = (
                            matches[target_idx][0], -1, matches[target_idx][2], '', matches[target_idx][4])
                        # print("update",target,"with valid range",r,"VAL",matches[target_idx])

                        prev_utt_id = matches[i][1]
                        continue

                    if matches[to_r][1] == -1:
                        target_idx = i
                        target = matches[target_idx]

                        r = (matches[from_r][1], matches[from_r][1])

                        if target[0] in alternatives and r[0] < alternatives[target[0]][0][1] < r[1]:
                            # print("update",target,"with valid range",r,"VAL",alternatives[target[0]][0])
                            matches[target_idx] = alternatives[target[0]][0]
                        else:
                            matches[target_idx] = (
                            matches[target_idx][0], -1, matches[target_idx][2], '', matches[target_idx][4])
                        # print("update",target,"with valid range",r,"VAL",matches[target_idx])

                        prev_utt_id = matches[from_r][1]
                        continue

                    if matches[from_r][1] - matches[to_r][1] < 0:
                        target_idx = i
                        target = matches[target_idx]
                        r = (matches[from_r][1], matches[to_r][1])

                        if target[0] in alternatives and r[0] < alternatives[target[0]][0][1] < r[1]:
                            # print("update",target,"with valid range",r,"VAL",alternatives[target[0]])
                            matches[target_idx] = alternatives[target[0]][0]
                        else:
                            matches[target_idx] = (
                            matches[target_idx][0], -1, matches[target_idx][2], '', matches[target_idx][4])
                        # print("update",target,"with valid range",r,"VAL",matches[target_idx])

                        prev_utt_id = matches[from_r][1]
                        continue
                    else:
                        target_idx = from_r
                        target = matches[target_idx]

                        from_r -= 1
                        while matches[from_r][1] == -1:
                            from_r -= 1

                        to_r -= 1
                        while matches[to_r][1] == -1:
                            to_r -= 1

                        r = (matches[from_r][1], matches[to_r][1])

                        if target[0] in alternatives and r[0] < alternatives[target[0]][0][1] < r[1]:
                            # print("update",target,"with valid range",r,"VAL",alternatives[target[0]])
                            matches[target_idx] = alternatives[target[0]][0]
                        else:
                            matches[target_idx] = (
                            matches[target_idx][0], -1, matches[target_idx][2], '', matches[target_idx][4])
                        # print("update",target,"with valid range",r,"VAL",matches[target_idx])

                        prev_utt_id = matches[from_r][1]
                        continue

                prev_utt_id = curr_utt_id

            # At this point, all matches have been corrected. Now we can produce the segments according to the matches.
            if subject not in self._segments_by_subject:
                self._segments_by_subject[subject] = []

            _, utterance_id, _, _, _ = matches[0]
            curr_cntxt = 'nonrequest'
            if utterance_id != -1:
                curr_cntxt = car[utterance_id]
            prev_cntxt = curr_cntxt
            # print("<BOUNDARY>")
            start = end = 0
            # print(matches[0])
            for i in range(1, len(matches)):
                match = matches[i]
                _, utterance_id, _, _, _ = match

                if utterance_id != -1:
                    curr_cntxt = car[utterance_id]
                else:
                    curr_cntxt = 'nonrequest'

                if (prev_cntxt == 'request' and curr_cntxt == 'request') or \
                        (prev_cntxt == 'request' and curr_cntxt == 'nonrequest') or \
                        (prev_cntxt == 'nonrequest' and curr_cntxt != 'nonrequest') or \
                        (prev_cntxt == 'conclusion' and curr_cntxt != 'conclusion'):
                    # print("<BOUNDARY>")
                    end = i
                    self._segments_by_subject[subject].append(matches[start:end])
                # print(curr_cntxt,match)
                prev_cntxt = curr_cntxt
                start = end
            self._segments_by_subject[subject].append(matches[start:])
        return self._segments_by_subject
