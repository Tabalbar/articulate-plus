from .segmenter import Segmenter


class TextSegmenter(Segmenter):
    def __init__(self, utterances_by_subject, top_trained_model, bottom_trained_model, dialogue_act_model):
        super().__init__()

        # model used for segmenting
        self._top_trained_model = top_trained_model
        self._bottom_trained_model = bottom_trained_model
        self._dialogue_act_model = dialogue_act_model

        # note, this must be spacy object utterances not string utterances. This is because
        # we need to extract named entities from the utterances to determine if it contains data attributes.
        self._utterances_by_subject = utterances_by_subject

    # predict dialogue act
    def _predict_dialogue_act(self, utterances):
        return self._dialogue_act_model.predict(
            top_level_trained_model=self._top_trained_model,
            bottom_level_trained_model=self._bottom_trained_model,
            context_utterances=[s[4] for s in utterances]).get_top_level()[-1]

    # does a given utterance contain data attributes.
    def _has_data_attrs(self, utterance):
        return utterance._.entities != []

    def get_segments_by_subject(self, unseen_subjects, fold=0):
        if self._segments_by_subject:
            return self._segments_by_subject

        boundary_end = -1
        for subject, utterances_data in self._utterances_by_subject.items():
            if subject not in unseen_subjects:
                continue

            print("Segmenting", subject)

            if subject not in self._segments_by_subject:
                self._segments_by_subject[subject] = []

            start = current_utterance_id = 0
            processed = []
            while current_utterance_id < len(utterances_data):
                # start of a new context window.
                current_utterance_id = start

                if current_utterance_id >= len(utterances_data):
                    continue

                # start and end boundaries aligned with current utterance.
                boundary_start = boundary_end = current_utterance_id
                line_id, utterance_id, utterance, ar, utterance_obj = utterances_data[current_utterance_id]

                # listen to stream until a data attribrute has been detected.
                # start_window = ['u','u','u',...,'d'] or start_window = ['u','u','u',...,'r']
                start_window = []
                while not self._has_data_attrs(utterance_obj):
                    start_window.append((line_id, utterance_id, utterance, ar, utterance_obj))
                    current_utterance_id += 1

                    if current_utterance_id >= len(utterances_data):
                        break

                    line_id, utterance_id, utterance, ar, utterance_obj = utterances_data[current_utterance_id]
                start_window.append((line_id, utterance_id, utterance, ar, utterance_obj))

                # predict da to determine if we are dealing with ['u','u','u','d'] or ['u','u','u','r'].
                # if start_window = ['u','u','u',...,'r'], it means setup+request = ['u,','u','u','r'].
                # if start_window = ['u','u','u',...,'d'], it means setup = ['d'] and adding
                # ['u','u','u'] as a separate segment.
                dialogue_act = self._predict_dialogue_act(start_window)
                processed += start_window
                if dialogue_act != 'merged' or not self._has_data_attrs(utterance_obj):
                    # since start of new window, we need to add previous context window first, i.e.,
                    # previous context window = ['u,'u','u'].
                    boundary_end = current_utterance_id - 1
                    self._segments_by_subject[subject].append((processed[boundary_start:boundary_end + 1]))
                    boundary_start = current_utterance_id

                    # now we are at start of new context window, i.e., setup. add to context until request is found,
                    # i.e., setup+request = ['d', ..., 'r'].
                    dialogue_act = 'setup'
                    while dialogue_act != 'merged':
                        current_utterance_id += 1

                        if current_utterance_id >= len(utterances_data):
                            break

                        line_id, utterance_id, utterance, ar, utterance_obj = utterances_data[current_utterance_id]
                        processed.append((line_id, utterance_id, utterance, ar, utterance_obj))
                        dialogue_act = self._predict_dialogue_act(processed[boundary_start:])

                # now setup+request = ['u',...,'u','r'] or setup+request=['d',...,'r']
                # next compute the conclusion part of segment.
                current_utterance_id += 1
                if current_utterance_id >= len(utterances_data):
                    # simply add setup+request as a segment since no more utterances remain for processing.
                    if dialogue_act == 'merged' and boundary_start <= boundary_end:
                        processed.append((line_id, utterance_id, utterance, ar, utterance_obj))
                        self._segments_by_subject[subject].append(
                            processed[boundary_start:boundary_end + 1])
                    continue

                # keep adding utterances as part of conclusion.
                line_id, utterance_id, utterance, ar, utterance_obj = utterances_data[current_utterance_id]
                processed.append((line_id, utterance_id, utterance, ar, utterance_obj))
                dialogue_act = self._predict_dialogue_act(processed[boundary_start:])
                while dialogue_act is not 'merged' and not self._has_data_attrs(utterance_obj):
                    current_utterance_id += 1

                    if current_utterance_id >= len(utterances_data):
                        break

                    line_id, utterance_id, utterance, ar, utterance_obj = utterances_data[current_utterance_id]
                    processed.append((line_id, utterance_id, utterance, ar, utterance_obj))
                    dialogue_act = self._predict_dialogue_act(processed[boundary_start:])

                # context window is complete, however need to modify if request detected:
                # when context window = ['u,'u','u','r','u','u'...,'r'] then modify conclusion so that we add
                # segment = ['u','u','u','r','u',..,'u'] and start new context window = ['r'] (processing to start of loop).
                # when context window = ['d',...,'r','u','u',...,'d'] then just add the whole context window as a segment,
                # i.e., segment = ['d',...,'r','u','u',...,'d']
                if dialogue_act == 'merged':
                    processed.pop()
                    if current_utterance_id >= len(utterances_data):
                        current_utterance_id -= 1
                    start = current_utterance_id
                    boundary_end = current_utterance_id
                    self._segments_by_subject[subject].append(processed[boundary_start:boundary_end + 1])
                else:
                    start = current_utterance_id + 1
                    boundary_end = current_utterance_id
                    self._segments_by_subject[subject].append(processed[boundary_start:boundary_end + 1])

            # add remaining unprocessed utterances as a final segment.
            if boundary_end + 1 < len(processed) - 1:
                self._segments_by_subject[subject].append(processed[boundary_end + 1:])

        return self._segments_by_subject