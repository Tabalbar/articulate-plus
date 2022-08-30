class Annotation:
    def __init__(self, annotation):
        self.attribute_data = None
        self.attributes = None

        if annotation is not None:
            self.attribute_data = annotation[u'attribute']

    def get_attributes(self):
        return self.attributes

    def __str__(self):
        return str(self.attributes)


class Utterance(Annotation):
    UTTERANCETYPE_IDX = 0
    UTTERANCEID_IDX = 1
    TIMESTEP_IDX = 2
    UTTERANCE_IDX = 3

    def __init__(self, annotation, attributes=None):
        super().__init__(annotation)

        if annotation is not None:
            utterancetype_attribute = str(self.attribute_data[Utterance.UTTERANCETYPE_IDX][u'__text']).lower()
            utteranceid_attribute = str(self.attribute_data[Utterance.UTTERANCEID_IDX][u'__text']).lower()
            timestep_attribute = str(self.attribute_data[Utterance.TIMESTEP_IDX][u'__text']).lower()
            utterance_attribute = str(self.attribute_data[Utterance.UTTERANCE_IDX][u'__text'])

            self.attributes = [utterancetype_attribute, utteranceid_attribute, timestep_attribute, utterance_attribute]
        else:
            self.attributes = attributes

    def get_utterancetype_attribute(self):
        return self.attributes[Utterance.UTTERANCETYPE_IDX]

    def get_utteranceid_attribute(self):
        return self.attributes[Utterance.UTTERANCEID_IDX]

    def get_timestep_attribute(self):
        return self.attributes[Utterance.TIMESTEP_IDX]

    def get_utterance_attribute(self):
        return self.attributes[Utterance.UTTERANCE_IDX]

    def set_utterance_attribute(self, utterance):
        self.attributes[Utterance.UTTERANCE_IDX] = utterance

    def __str__(self):
        s = ''
        for attribute in self.attributes:
            if attribute and type(attribute) == list:
                s += str(attribute[0])
            else:
                s += str(attribute)
            s += ', '
        s = s[:-2]
        return s


class Gesture(Annotation):
    MODE_IDX = 0
    GESTUREID_IDX = 1
    UTTERANCEID_IDX = 2
    TIMESTEP_IDX = 3
    TYPE_IDX = 4
    SPACE_IDX = 5
    TARGET_IDX = 6

    def __init__(self, annotation, attributes=None):
        super().__init__(annotation)

        if annotation is not None:
            mode_attribute = str(self.attribute_data[Gesture.MODE_IDX][u'__text']).lower()
            gestureid_attribute = str(self.attribute_data[Gesture.GESTUREID_IDX][u'__text']).lower()
            utteranceid_attribute = str(self.attribute_data[Gesture.UTTERANCEID_IDX][u'__text']).lower()
            timestep_attribute = str(self.attribute_data[Gesture.TIMESTEP_IDX][u'__text']).lower()
            type_attribute = str(self.attribute_data[Gesture.TYPE_IDX][u'__text']).lower()
            space_attribute = str(self.attribute_data[Gesture.SPACE_IDX][u'__text']).lower()
            target_attribute = str(self.attribute_data[Gesture.TARGET_IDX][u'__text']).lower()

            self.attributes = [mode_attribute, gestureid_attribute, utteranceid_attribute, timestep_attribute,
                               type_attribute, space_attribute, target_attribute]
        else:
            self.attributes = attributes

    def get_mode_attribute(self):
        return self.attributes[Gesture.MODE_IDX]

    def get_gestureid_attribute(self):
        return self.attributes[Gesture.GESTUREID_IDX]

    def get_utteranceid_attribute(self):
        return self.attributes[Gesture.UTTERANCEID_IDX]

    def get_timestep_attribute(self):
        return self.attributes[Gesture.TIMESTEP_IDX]

    def get_type_attribute(self):
        return self.attributes[Gesture.TYPE_IDX]

    def get_space_attribute(self):
        return self.attributes[Gesture.SPACE_IDX]

    def get_target_attribute(self):
        return self.attributes[Gesture.TARGET_IDX]

    def __str__(self):
        s = ''
        for attribute in self.attributes:
            if attribute and type(attribute) == list:
                s += str(attribute[0])
            else:
                s += str(attribute)
            s += ', '
        s = s[:-2]
        return s


class ReferringExpression(Annotation):
    TARGETVIS_IDS_IDX = 0
    GESTUREID_IDX = 1
    UTTERANCEID_IDX = 2
    REFERRINGEXPRESSIONID_IDX = 3
    TIMESTEP_IDX = 4
    TARGETVIS_PLOTTYPES_IDX = 5
    REFERRINGEXPRESSION_IDX = 6
    TARGETVIS_TEMPORALS_IDX = 7

    def __init__(self, annotation, attributes=None):
        super().__init__(annotation)

        if annotation is not None:
            targetvis_ids_attribute = str(self.attribute_data[ReferringExpression.TARGETVIS_IDS_IDX][u'__text']).lower()
            gestureid_attribute = str(self.attribute_data[ReferringExpression.GESTUREID_IDX][u'__text']).lower()
            utteranceid_attribute = str(self.attribute_data[ReferringExpression.UTTERANCEID_IDX][u'__text']).lower()
            referringexpressionid_attribute = str(
                self.attribute_data[ReferringExpression.REFERRINGEXPRESSIONID_IDX][u'__text']).lower()
            timestep_attribute = str(self.attribute_data[ReferringExpression.TIMESTEP_IDX][u'__text']).lower()
            targetvis_plottypes_attribute = str(
                self.attribute_data[ReferringExpression.TARGETVIS_PLOTTYPES_IDX][u'__text']).lower()
            referringexpression_attribute = str(
                self.attribute_data[ReferringExpression.REFERRINGEXPRESSION_IDX][u'__text']).lower()
            targetvis_temporals_attribute = str(
                self.attribute_data[ReferringExpression.TARGETVIS_TEMPORALS_IDX][u'__text']).lower()

            self.attributes = [targetvis_ids_attribute, gestureid_attribute, utteranceid_attribute,
                               referringexpressionid_attribute, timestep_attribute, targetvis_plottypes_attribute,
                               referringexpression_attribute, targetvis_temporals_attribute]
        else:
            self.attributes = attributes

    def get_sourcevis_ids_attribute(self):
        return None

    def get_targetvis_ids_attribute(self):
        return self.attributes[ReferringExpression.TARGETVIS_IDS_IDX]

    def get_gestureid_attribute(self):
        return self.attributes[ReferringExpression.GESTUREID_IDX]

    def get_utteranceid_attribute(self):
        return self.attributes[ReferringExpression.UTTERANCEID_IDX]

    def get_referringexpressionid_attribute(self):
        return self.attributes[ReferringExpression.REFERRINGEXPRESSIONID_IDX]

    def get_timestep_attribute(self):
        return self.attributes[ReferringExpression.TIMESTEP_IDX]

    def get_sourcevis_plottypes_attribute(self):
        return None

    def get_targetvis_plottypes_attribute(self):
        return self.attributes[ReferringExpression.TARGETVIS_PLOTTYPES_IDX]

    def get_referringexpression_attribute(self):
        return self.attributes[ReferringExpression.REFERRINGEXPRESSION_IDX]

    def set_referringexpression_attribute(self, referringexpression):
        self.attributes[ReferringExpression.REFERRINGEXPRESSION_IDX] = \
            referringexpression

    def get_targetvis_temporals_attribute(self):
        return self.attributes[ReferringExpression.TARGETVIS_TEMPORALS_IDX]

    def get_properties_attribute(self):
        return None

    def __str__(self):
        s = ''
        for attribute in self.attributes:
            if attribute and type(attribute) == list:
                s += str(attribute[0])
            else:
                s += str(attribute)
            s += ', '
        s = s[:-2]
        return s


class VisualizationReference(Annotation):
    UTTERANCEID_IDX = 0
    TARGETIDS_IDX = 1
    TIMESTEP_IDX = 2
    SOURCEIDS_IDX = 3
    SOURCE_PLOTTYPES_IDX = 4
    TARGET_PLOTTYPES_IDX = 5
    REFERRINGEXPRESSION_IDX = 6
    REFERRINGEXPRESSIONID_IDX = 7
    PROPERTIES_IDX = 8

    def __init__(self, annotation, attributes=None):
        super().__init__(annotation)

        if annotation is not None:
            utteranceid_attribute = str(self.attribute_data[VisualizationReference.UTTERANCEID_IDX][u'__text']).lower()
            targetids_attribute = str(self.attribute_data[VisualizationReference.TARGETIDS_IDX][u'__text']).lower()
            timestep_attribute = str(self.attribute_data[VisualizationReference.TIMESTEP_IDX][u'__text']).lower()
            sourceids_attribute = str(self.attribute_data[VisualizationReference.SOURCEIDS_IDX][u'__text']).lower()
            source_plottypes_attribute = str(
                self.attribute_data[VisualizationReference.SOURCE_PLOTTYPES_IDX][u'__text']).lower()
            target_plottypes_attribute = str(
                self.attribute_data[VisualizationReference.TARGET_PLOTTYPES_IDX][u'__text']).lower()
            referringexpression_attribute = str(
                self.attribute_data[VisualizationReference.REFERRINGEXPRESSION_IDX][u'__text']).lower()
            referringexpressionid_attribute = str(
                self.attribute_data[VisualizationReference.REFERRINGEXPRESSIONID_IDX][u'__text']).lower()
            properties_attribute = str(
                self.attribute_data[VisualizationReference.PROPERTIES_IDX][u'__text']).lower()

            self.attributes = [utteranceid_attribute, targetids_attribute, timestep_attribute, sourceids_attribute,
                               source_plottypes_attribute, target_plottypes_attribute, referringexpression_attribute,
                               referringexpressionid_attribute, properties_attribute]
        else:
            self.attributes = attributes

    def get_utteranceid_attribute(self):
        return self.attributes[VisualizationReference.UTTERANCEID_IDX]

    def get_targetvis_ids_attribute(self):
        return self.attributes[VisualizationReference.TARGETIDS_IDX]

    def get_timestep_attribute(self):
        return self.attributes[VisualizationReference.TIMESTEP_IDX]

    def get_sourcevis_ids_attribute(self):
        return self.attributes[VisualizationReference.SOURCEIDS_IDX]

    def get_sourcevis_plottypes_attribute(self):
        return self.attributes[VisualizationReference.SOURCE_PLOTTYPES_IDX]

    def get_targetvis_plottypes_attribute(self):
        return self.attributes[VisualizationReference.TARGET_PLOTTYPES_IDX]

    def get_referringexpression_attribute(self):
        return self.attributes[VisualizationReference.REFERRINGEXPRESSION_IDX]

    def set_referringexpression_attribute(self, referringexpression):
        self.attributes[VisualizationReference.REFERRINGEXPRESSION_IDX] = referringexpression

    def get_referringexpressionid_attribute(self):
        return self.attributes[VisualizationReference.REFERRINGEXPRESSIONID_IDX]

    def set_properties_attribute(self, properties):
        self.attributes[VisualizationReference.PROPERTIES_IDX] = properties

    def get_properties_attribute(self):
        return self.attributes[VisualizationReference.PROPERTIES_IDX]

    def __str__(self):
        s = ''
        for attribute in self.attributes:
            if attribute and type(attribute) == list:
                s += str(attribute[0])
            else:
                s += str(attribute)
            s += ', '
        s = s[:-2]
        return s
