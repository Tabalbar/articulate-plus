class ContextComponent:
    def __init__(self, utterance, gesture, gesture_based_referring_expression, text_based_referring_expression,
                 visualization_reference):
        self.utterance = utterance
        self.gesture = gesture
        self.gesture_based_referring_expression = gesture_based_referring_expression
        self.text_based_referring_expression = text_based_referring_expression
        self.visualization_reference = visualization_reference

    def get_utterance(self):
        return self.utterance

    def get_gesture(self):
        return self.gesture

    def get_gesture_based_referring_expression(self):
        return self.gesture_based_referring_expression

    def get_text_based_referring_expression(self):
        return self.text_based_referring_expression

    def get_visualization_reference(self):
        return self.visualization_reference

    def get_context_component(self):
        return self.get_utterance(), \
               self.get_gesture(), \
               self.get_gesture_based_referring_expression(), \
               self.get_text_based_referring_expression(), \
               self.get_visualization_reference()

    def get_context_component_as_json(self):
        component = dict()
        if self.get_utterance() is not None:
            component['utterance'] = self.get_utterance().get_attributes()
        else:
            component['utterance'] = None

        if self.get_gesture() is not None:
            component['gesture'] = []
            for gesture in self.get_gesture():
                component['gesture'].append(gesture.get_attributes())
        else:
            component['gesture'] = None

        if self.get_gesture_based_referring_expression() is not None:
            component['gesture_based_referring_expression'] = []
            for refexp in self.get_gesture_based_referring_expression():
                component['gesture_based_referring_expression'].append(refexp.get_attributes())
        else:
            component['gesture_based_referring_expression'] = None

        if self.get_text_based_referring_expression() is not None:
            component['text_based_referring_expression'] = []
            for refexp in self.get_text_based_referring_expression():
                component['text_based_referring_expression'].append(refexp.get_attributes())
        else:
            component['text_based_referring_expression'] = None

        if self.get_visualization_reference() is not None:
            component['visualization_reference'] = []
            for refexp in self.get_visualization_reference():
                component['visualization_reference'].append(refexp.get_attributes())
        else:
            component['visualization_reference'] = None

        return component

    def __str__(self):
        utterance, gesture, gesture_based_referring_expression, text_based_referring_expression, visualization_reference = self.get_context_component()
        s = '\n'
        s += '    UTT [' + str(utterance) + ']\n'
        if gesture is not None:
            s += '    GST ' + str([[str(g)] for g in gesture]) + '\n'
        else:
            s += '    GST [None]\n'

        if gesture_based_referring_expression is not None:
            s += '    GSTRE ' + str([[str(r)] for r in gesture_based_referring_expression]) + '\n'
        else:
            s += '    GSTRE [None]\n'

        if text_based_referring_expression is not None:
            s += '    TXTRE ' + str([[str(r)] for r in text_based_referring_expression]) + '\n'
        else:
            s += '    TXTRE [None]\n'

        if visualization_reference is not None:
            s += '    VSREF ' + str([[str(v)] for v in visualization_reference]) + '\n'
        else:
            s += '    VSREF [None]\n'
        return s


class Context:
    def __init__(self):
        self.setup = []
        self.request = None
        self.conclusion = []

    def add_to_setup(self, setup):
        self.setup.append(setup)

    def set_request(self, request):
        self.request = request

    def add_to_conclusion(self, conclusion):
        self.conclusion.append(conclusion)

    def get_setup(self):
        return self.setup

    def get_request(self):
        return self.request

    def get_conclusion(self):
        return self.conclusion

    def get_context(self):
        return self.get_setup(), self.get_request(), self.get_conclusion()

    def __str__(self):
        s = 'CONTEXT [\n'
        if self.setup is None:
            s += '  SETUP [None]\n'
        else:
            s += '  SETUP ['
            for item in self.setup:
                s += str(item)
            s += '  ]\n'
        if self.request is None:
            s += '  REQUEST [None]\n'
        else:
            s += '  REQUEST ['
            s += str(self.request)
            s += '  ]\n'
        if self.conclusion is None:
            s += '  CONCLUSION [None]\n'
        else:
            s += '  CONCLUSION ['
            for item in self.conclusion:
                s += str(item)
            s += '  ]\n'
        s += ']\n'
        return s
