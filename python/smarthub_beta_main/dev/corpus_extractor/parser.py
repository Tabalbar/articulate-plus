import json

from nltk.tokenize import word_tokenize

from .corpusannotations.annotation_extractions import GesturesAnnotationExtractor
from .corpusannotations.annotation_extractions import ReferringExpressionsAnnotationExtractor
from .corpusannotations.annotation_extractions import UtterancesAnnotationExtractor
from .corpusannotations.annotation_extractions import VisualizationReferencesAnnotationExtractor
from .corpusannotations.context_annotations import Context
from .corpusannotations.context_annotations import ContextComponent
from .corpusannotations.dialogue_annotations import ReferringExpression
from .corpusannotations.dialogue_annotations import Utterance, Gesture, VisualizationReference
from .corpusannotations.referring_expression_info import ReferringExpressionInfo
from .utterance_processing_utils import UtteranceProcessingUtils
from ..text_tokenizer_pipeline.text_processing_utils import TextProcessingUtils


class Parser:
    utterance_annotations = None
    gesture_annotations = None
    referring_expression_annotations = None
    visualization_reference_annotations = None

    @staticmethod
    def create_context_component_from_json(context_component_as_json, process_refexps=True):
        utterance = Utterance(annotation=None, attributes=context_component_as_json['utterance'])

        if context_component_as_json['gesture'] is not None:
            gesture = [Gesture(annotation=None, attributes=cc) for cc in context_component_as_json['gesture']]
        else:
            gesture = None

        if context_component_as_json['gesture_based_referring_expression'] is not None:
            gesture_based_referring_expression = [ReferringExpression(annotation=None, attributes=cc) \
                                                  for cc in
                                                  context_component_as_json['gesture_based_referring_expression']]
            if process_refexps:
                Parser.process_referring_expressions(utterance.get_utterance_attribute(),
                                                     gesture_based_referring_expression)
        else:
            gesture_based_referring_expression = None

        if context_component_as_json['text_based_referring_expression'] is not None:
            text_based_referring_expression = [ReferringExpression(annotation=None, attributes=cc) \
                                               for cc in context_component_as_json['text_based_referring_expression']]
            if process_refexps:
                Parser.process_referring_expressions(utterance.get_utterance_attribute(),
                                                     text_based_referring_expression)
        else:
            text_based_referring_expression = None

        if context_component_as_json['visualization_reference'] is not None:
            visualization_reference = [VisualizationReference(annotation=None, attributes=cc) \
                                       for cc in context_component_as_json['visualization_reference']]
            if process_refexps:
                Parser.process_referring_expressions(utterance.get_utterance_attribute(),
                                                     visualization_reference)
        else:
            visualization_reference = None

        return ContextComponent(
            utterance=utterance,
            gesture=gesture,
            gesture_based_referring_expression=gesture_based_referring_expression,
            text_based_referring_expression=text_based_referring_expression,
            visualization_reference=visualization_reference)

    @staticmethod
    def parse_from_json(subject_json, process_refexps=True):
        for context_json in subject_json:
            context = Context()

            setup = context_json['setup']
            for context_component_as_json in setup:
                context_component = Parser.create_context_component_from_json(
                    context_component_as_json=context_component_as_json,
                    process_refexps=process_refexps)
                context.add_to_setup(context_component)

            request = context_json['request']
            for context_component_as_json in request:
                context_component = Parser.create_context_component_from_json(
                    context_component_as_json=context_component_as_json,
                    process_refexps=process_refexps)
                context.set_request(context_component)

            conclusion = context_json['conclusion']
            for context_component_as_json in conclusion:
                context_component = Parser.create_context_component_from_json(
                    context_component_as_json=context_component_as_json,
                    process_refexps=process_refexps)
                context.add_to_conclusion(context_component)

            yield context

    @staticmethod
    def _find_all_occurrences(input_str, search_str):
        l1 = []
        length = len(input_str)
        index = 0
        input_str_processed = TextProcessingUtils.clean_text(
            text=input_str, remove_punctuation=True).lower()
        search_str_processed = TextProcessingUtils.clean_text(
            text=search_str, remove_punctuation=True).lower()
        while index < length:
            i = input_str_processed.find(search_str_processed, index)
            if i == -1:
                return l1
            start = len(input_str_processed[:i].split())
            end = start + len(search_str_processed.split())
            if ' '.join(input_str_processed.split()[start:end]) != search_str_processed:
                index = i + 1
                continue
            l1.append(start)
            index = i + 1
        return l1

    @staticmethod
    def process_referring_expressions(utterance, referringexpressions):
        processed_utterance = TextProcessingUtils.clean_text(text=utterance, remove_punctuation=True).lower()
        for referringexpression in referringexpressions:
            referring_expression_attribute = referringexpression.get_referringexpression_attribute()
            referring_expression_id = referringexpression.get_referringexpressionid_attribute()
            referring_expression_targets = referringexpression.get_targetvis_ids_attribute()
            #referring_expression_properties = referringexpression.get_properties_attribute()

            if referring_expression_attribute == 'none':
                referringexpression.set_referringexpression_attribute([])
                continue

            referring_expression_attribute = \
                referring_expression_attribute[1:len(referring_expression_attribute) - 1]

            processed_referring_expressions = []
            for refexp in referring_expression_attribute.split(';'):
                refexp_arr = refexp.split('@@@')
                which_occurrence = int(refexp_arr[1]) - 1
                refexp_arr[0] = UtteranceProcessingUtils.clean_utterance(
                    TextProcessingUtils.clean_text(text=refexp_arr[0]), remove_hyphens=True)
                starts = Parser._find_all_occurrences(input_str=utterance, search_str=refexp_arr[0])

                if not starts:
                    continue

                words = refexp_arr[0].split()

                start_word_idx = starts[which_occurrence]
                word_offset = len(words)
                end_word_idx = start_word_idx + word_offset

                referring_expression_info = ReferringExpressionInfo()
                referring_expression_info.rid = referring_expression_id
                referring_expression_info.targets = referring_expression_targets
                #referring_expression_info.properties = referring_expression_properties

                for curr_idx in range(len(words)):
                    word = words[curr_idx]
                    if curr_idx == 0:
                        label = 'B-ref'
                    else:
                        label = 'I-ref'

                    curr_word_idx = start_word_idx + curr_idx
                    start_char_idx = len(' '.join(processed_utterance.split()[:curr_word_idx]))+1
                    end_char_idx = start_char_idx + len(word)

                    referring_expression_info.add(start_word_idx + curr_idx, start_char_idx, end_char_idx, word, label)

                processed_referring_expressions.append(referring_expression_info)

            referringexpression.set_referringexpression_attribute(
                processed_referring_expressions)

    @staticmethod
    def create_context_component(utteranceid, process_refexps):
        utterance = Parser.utterance_annotations.get_utterance(utteranceid)
        utterance.set_utterance_attribute(UtteranceProcessingUtils.clean_utterance(
            TextProcessingUtils.clean_text(text=utterance.get_utterance_attribute()),
            remove_hyphens=True))

        referringexpressions = \
            Parser.referring_expression_annotations.get_gesture_based_referring_expressions(utteranceid)
        if referringexpressions and process_refexps:
            Parser.process_referring_expressions(utterance.get_utterance_attribute(), referringexpressions)

        referringexpressions = \
            Parser.referring_expression_annotations.get_text_based_referring_expressions(utteranceid)
        if referringexpressions and process_refexps:
            Parser.process_referring_expressions(utterance.get_utterance_attribute(), referringexpressions)

        referringexpressions = \
            Parser.visualization_reference_annotations.get_visualization_references(utteranceid)
        if referringexpressions and process_refexps:
            Parser.process_referring_expressions(utterance.get_utterance_attribute(), referringexpressions)

        return ContextComponent(
            utterance=utterance,
            gesture=Parser.gesture_annotations.get_gestures(utteranceid),
            gesture_based_referring_expression=Parser.referring_expression_annotations.
            get_gesture_based_referring_expressions(utteranceid),
            text_based_referring_expression=Parser.referring_expression_annotations.
            get_text_based_referring_expressions(utteranceid),
            visualization_reference=Parser.visualization_reference_annotations.
            get_visualization_references(utteranceid))

    @staticmethod
    def parse(file_path, utterance_cutoff=4, process_refexps=True):
        with open(file_path, 'rt') as f:
            data = json.load(f)
        parsed_data = data[u'annotation'][u'body'][u'track']

        Parser.utterance_annotations = UtterancesAnnotationExtractor(data=parsed_data)
        Parser.gesture_annotations = GesturesAnnotationExtractor(data=parsed_data)
        Parser.referring_expression_annotations = ReferringExpressionsAnnotationExtractor(data=parsed_data)
        Parser.visualization_reference_annotations = VisualizationReferencesAnnotationExtractor(data=parsed_data)

        utteranceids = Parser.utterance_annotations.get_utteranceids()
        index = 0
        while index < len(utteranceids):
            utteranceid = utteranceids[index]
            timestep = Parser.utterance_annotations.get_utterance(utteranceid).get_timestep_attribute()

            context = Context()
            while timestep == 'previous':
                component = Parser.create_context_component(utteranceid, process_refexps)
                if len(word_tokenize(
                        component.get_utterance().get_utterance_attribute())) >= utterance_cutoff:
                    context.add_to_setup(component)
                else:
                    print("SKIPPING", component.get_utterance().get_utterance_attribute())

                index += 1
                if index >= len(utteranceids):
                    timestep = None
                    break

                utteranceid = utteranceids[index]
                timestep = Parser.utterance_annotations.get_utterance(utteranceid).get_timestep_attribute()
                continue

            if timestep == 'current':
                component = Parser.create_context_component(utteranceid, process_refexps)
                if len(word_tokenize(
                        component.get_utterance().get_utterance_attribute())) >= utterance_cutoff:
                    context.set_request(component)
                else:
                    print("SKIPPING", component.get_utterance().get_utterance_attribute())

                index += 1
                if index >= len(utteranceids):
                    timestep = None
                    break

                utteranceid = utteranceids[index]
                timestep = Parser.utterance_annotations.get_utterance(utteranceid).get_timestep_attribute()

            while timestep == 'next':
                component = Parser.create_context_component(utteranceid, process_refexps)
                if len(word_tokenize(
                        component.get_utterance().get_utterance_attribute())) >= utterance_cutoff:
                    context.add_to_conclusion(component)
                else:
                    print("SKIPPING", component.get_utterance().get_utterance_attribute())

                index += 1
                if index >= len(utteranceids):
                    timestep = None
                    break

                utteranceid = utteranceids[index]
                timestep = Parser.utterance_annotations.get_utterance(utteranceid).get_timestep_attribute()
                continue
            if context.get_request() is not None:
                yield context
