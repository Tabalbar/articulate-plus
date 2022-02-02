from collections import OrderedDict

from .dialogue_annotations import Gesture
from .dialogue_annotations import ReferringExpression
from .dialogue_annotations import Utterance
from .dialogue_annotations import VisualizationReference


class AnnotationIndex:
    UTTERANCES_IDX = 0
    GESTURES_IDX = 1
    REFERRING_EXPRESSIONS_IDX = 2
    VISUALIZATION_REFERENCES_IDX = 3


class AnnotationExtractor:
    def __init__(self, data):
        self.annotations = OrderedDict()

    def get_annotations(self):
        return self.annotations


class UtterancesAnnotationExtractor(AnnotationExtractor):
    def __init__(self, data):
        super().__init__(data)

        for utterance_data in data[AnnotationIndex.UTTERANCES_IDX][u'el']:
            utterance = Utterance(utterance_data)

            utteranceid = utterance.get_utteranceid_attribute()
            self.annotations[utteranceid] = utterance

    def get_utteranceids(self):
        return list(self.annotations.keys())

    def get_utterances(self):
        return list(self.annotations.values())

    def get_utterance(self, utteranceid):
        if utteranceid not in self.annotations:
            return None
        return self.annotations[utteranceid]

    def __str__(self):
        s = ''
        for key, value in self.annotations.items():
            s += str(key) + ' : '
            s += str(value) + ', '
        s = s[:-2]
        return s


class GesturesAnnotationExtractor(AnnotationExtractor):
    def __init__(self, data):
        super().__init__(data)

        for gesture_data in data[AnnotationIndex.GESTURES_IDX][u'el']:
            gesture = Gesture(gesture_data)

            utteranceid = gesture.get_utteranceid_attribute()
            if utteranceid not in self.annotations:
                self.annotations[utteranceid] = OrderedDict()

            gestureid = gesture.get_gestureid_attribute()
            if gestureid not in self.annotations[utteranceid]:
                self.annotations[utteranceid][gestureid] = []
            self.annotations[utteranceid][gestureid].append(gesture)

    def get_utteranceids(self):
        return list(self.annotations.keys())

    def get_gestureids(self, utteranceid):
        if utteranceid not in self.annotations:
            return None
        return list(self.annotations[utteranceid].keys())

    def get_gestures(self, utteranceid):
        if utteranceid not in self.annotations:
            return None
        data = []
        for key, values in self.annotations[utteranceid].items():
            for value in values:
                data.append(value)
        return data

    def get_gesture(self, utteranceid, gestureid):
        if utteranceid not in self.annotations:
            return None
        if gestureid not in self.annotations[utteranceid]:
            return None
        return self.annotations[utteranceid][gestureid]

    def __str__(self):
        s = ''
        for key, values in self.annotations.items():
            s += str(key) + ' : '
            for value in values:
                s += str(value) + ', '
            s = s[:-2]
            s += '\n'
        return s


class ReferringExpressionsAnnotationExtractor(AnnotationExtractor):
    def __init__(self, data):
        super().__init__(data)

        self.gesture_based_referring_expressions = OrderedDict()
        self.text_based_referring_expressions = OrderedDict()

        for referring_expression_data in data[AnnotationIndex.REFERRING_EXPRESSIONS_IDX][u'el']:
            referring_expression = ReferringExpression(referring_expression_data)

            utteranceid = referring_expression.get_utteranceid_attribute()
            if utteranceid not in self.annotations:
                self.annotations[utteranceid] = OrderedDict()

            gestureid = referring_expression.get_gestureid_attribute()

            if gestureid == 'none':
                # referring expression without a gestureid means it is a text-based reference.
                if utteranceid not in self.text_based_referring_expressions:
                    self.text_based_referring_expressions[utteranceid] = []
                self.text_based_referring_expressions[utteranceid].append(referring_expression)

                if -1 not in self.annotations[utteranceid]:
                    self.annotations[utteranceid][-1] = []
                self.annotations[utteranceid][-1].append(referring_expression)

            else:
                # otherwise it is a gesture-based reference (i.e., no referring expression can be
                # both a gesture and text-based reference, must only be one or the other reference).
                if utteranceid not in self.gesture_based_referring_expressions:
                    self.gesture_based_referring_expressions[utteranceid] = OrderedDict()
                if gestureid not in self.gesture_based_referring_expressions[utteranceid]:
                    self.gesture_based_referring_expressions[utteranceid][gestureid] = []
                self.gesture_based_referring_expressions[utteranceid][gestureid].append(referring_expression)

                if gestureid not in self.annotations[utteranceid]:
                    self.annotations[utteranceid][gestureid] = []
                self.annotations[utteranceid][gestureid].append(referring_expression)

    def get_utteranceids(self):
        return list(self.annotations.keys())

    def get_gestureids(self, utteranceid):
        return list(self.annotations[utteranceid].keys())

    def get_referring_expressions(self, utteranceid):
        if utteranceid not in self.annotations:
            return None
        return list(self.annotations[utteranceid].values())

    def get_referring_expression(self, utteranceid, gestureid):
        if utteranceid not in self.annotations:
            return None
        if gestureid not in self.annotations[utteranceid]:
            return None
        return self.annotations[utteranceid][gestureid]

    def get_gesture_based_referring_expressions_utteranceids(self):
        return list(self.gesture_based_referring_expressions.keys())

    def get_gesture_based_referring_expressions_gestureids(self, utteranceid):
        if utteranceid not in self.gesture_based_referring_expressions:
            return None
        return list(self.gesture_based_referring_expressions[utteranceid].keys())

    def get_gesture_based_referring_expressions(self, utteranceid):
        if utteranceid not in self.gesture_based_referring_expressions:
            return None
        data = []
        for key, values in self.gesture_based_referring_expressions[utteranceid].items():
            for value in values:
                data.append(value)
        return data

    def get_gesture_based_referring_expression(self, utteranceid, gestureid):
        if utteranceid not in self.gesture_based_referring_expressions:
            return None
        if gestureid not in self.gesture_based_referring_expressions[utteranceid]:
            return None
        return self.gesture_based_referring_expressions[utteranceid][gestureid]

    def get_text_based_referring_expressions_utteranceids(self):
        return list(self.text_based_referring_expressions.keys())

    def get_text_based_referring_expressions(self, utteranceid):
        if utteranceid not in self.text_based_referring_expressions:
            return None

        return self.text_based_referring_expressions[utteranceid]

    def __str__(self):
        s = ''
        for key, values in self.text_based_referring_expressions.items():
            s += str(key) + ' : '
            for value in values:
                s += str(value) + ', '
            s = s[:-2]
            s += '\n'
        for key, values in self.gesture_based_referring_expressions.items():
            s += str(key) + ' : '
            for value in values:
                s += str(value) + ', '
            s = s[:-2]
            s += '\n'

        return s


class VisualizationReferencesAnnotationExtractor(AnnotationExtractor):
    def __init__(self, data):
        super().__init__(data)

        for visualization_reference_data in data[AnnotationIndex.VISUALIZATION_REFERENCES_IDX][u'el']:
            visualization_reference = VisualizationReference(visualization_reference_data)

            utteranceid = visualization_reference.get_utteranceid_attribute()
            if utteranceid not in self.annotations:
                self.annotations[utteranceid] = []
            self.annotations[utteranceid].append(visualization_reference)

    def get_utteranceids(self):
        return list(self.annotations.keys())

    def get_visualization_references(self, utteranceid):
        if utteranceid not in self.annotations:
            return None
        return self.annotations[utteranceid]

    def __str__(self):
        s = ''
        for key, value in self.annotations.items():
            s += str(key) + ' : '
            s += str(value) + ', '
        s = s[:-2]
        return s
