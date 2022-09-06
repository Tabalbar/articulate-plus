import copy
# import speech_recognition as sr
from collections import Sequence
from multiprocessing import Process

from app.language_understanding_models import LanguageUnderstandingModels
from app.state_tracker import StateTracker
from dev.corpus_feature_extractor.corpus_feature_extractor_utils import CorpusFeatureExtractorUtils
from run.online_mode.rule_engine_factory import RuleEngineFactory
from run.online_mode.rule_context import RuleContext


class ContextWindow(Sequence):
    def __init__(self, use_full_context_window_for_da_prediction=False):
        self.multimodal_data = []

        self.utterances = []
        self.gesture_target_vis_ids = []
        self.dialogue_acts = []
        self.referring_expressions = []

        self.has_request = False

        self.use_full_context_window_for_da_prediction = use_full_context_window_for_da_prediction

    def add(self, utterance, gesture_target_id, dialogue_act, referring_expressions):
        self.multimodal_data.append((utterance, gesture_target_id, dialogue_act, referring_expressions))
        self.utterances.append(utterance)
        self.gesture_target_vis_ids.append(gesture_target_id)
        self.dialogue_acts.append(dialogue_act)
        self.referring_expressions.append(referring_expressions)

        top_dialogue_act_label, bottom_dialogue_act_label = dialogue_act[0], dialogue_act[1]
        if top_dialogue_act_label == 'merged':
            self.has_request = True

    def __getitem__(self, index):
        return self.multimodal_data[index]

    def __len__(self):
        return len(self.multimodal_data)


class FakeKinectService:
    @staticmethod
    def observe_screen_pointing_gesture():
        # use kinect to detect hand pointing gesture
        return int(-1) #input('gesture: ')

# received audio data, now we'll recognize it using Google Speech Recognition
# for testing purposes, we're just using the default API key
        # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
        # instead of `r.recognize_google(audio)`
class FakeSpeechToTextService:
    @staticmethod
    def callback(recognizer, audio):
        try:
            print("Google Speech Recognition thinks you said " + recognizer.recognize_google(audio))
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))

    # @staticmethod
    # def speech_to_text():
    #     # use speech to text service to obtain next spoken utterance.
    #     r = sr.Recognizer()
    #     with sr.Microphone() as source:
    #         r.adjust_for_ambient_noise(source)
    #         print("Speak..")
    #         audio = r.listen(source)
    #         print("Speech to text.. ")


    #     # recognize speech using google

    #     try:

    #         speech_input = r.recognize_google(audio)
    #         print("Speech Input \n" + speech_input)



    #     except Exception as e:
    #         print("Error :  " + str(e))
    #     # input('utterance : ')
    #     return speech_input


class FakeMultimodalService:
    @staticmethod
    def listen():
        # keep waiting until spoken utterance is heard.
        utterance = FakeSpeechToTextService.speech_to_text()

        # once utterance is heard, also observe pointing gestures made towards the screen display.
        gesture_target_id = FakeKinectService.observe_screen_pointing_gesture()

        return utterance, gesture_target_id


class SmarthubSession:
    def __init__(self):
        # Step 1: instantiate NER which is our Spacy rule based NER. By running our NER, we can extract
        # data attributes\properties of a given utterance.
        corpus_entity_extractor = CorpusFeatureExtractorUtils.get_context_based_corpus_entity_extractor()
        self.entity_tokenizer = corpus_entity_extractor.get_tokenizer()

        # Step 2: load our state tracker for the purpose of dialogue state tracking.
        self.state_tracker = StateTracker()

        # Step 3.a: state variable for when data attribute was mentioned.
        self.found_data = False

        # Step 3.b: state variable for when conversation is in the conclusion state.
        self.conclusion_mode = False

        # Step 3.c: state variable for the current context (represents setup + request).
        self.context_window = ContextWindow()

    '''
    - The purpose of determine_best_action() method is to determine the best action to take given the current state of
     the dialogue. 

    - Algorithm flow:
    1. create curr spec from current context window (setup + request).
    2. if dialogue act is createvis (or preference, fact-based, clarification), then:
        add curr spec to dialogue history.
        recommend curr spec as best action to take.

    3. Otherwise if dialogue act is modifyvis, then:
        if co-occurring (gesture + ref exp), then:
            prev spec = dialogue_history[gesture target id]

        otherwise:
            prev spec = choose the spec that maximizes cosine_similarity(curr_spec, dialogue_history) >= 0.40.
                - if the spec maximizing cosine similarity is below 0.40 cutoff, ignore it.

            if no prev spec found still but ref exp exists:
                prev spec = choose most recent spec from dialogue history.

        if prev spec was found, then:
            inform curr spec of knowledge about filters and aggregates from prev spec.
            add curr spec to dialogue history.
            recommend curr spec as best action to take. 
        otherwise:
            no ref exp exists, so just add curr spec as is to the dialogue history.
            recommend curr spec as best action to take.

    4. Otherwise if dialogue act is winmgmt, then:
        if co-occurring (gesture + ref exp), then:
            prev spec = dialogue_history[gesture target id]    
        otherwise:
            prev spec = choose the spec that maximizes cosine_similarity(curr_spec, dialogue_history) > 0.10.
                - if the spec maximizing cosine similarity is below 0.10 cutoff, ignore it.

            if no prev spec found still but ref exp exists:
                prev spec = choose most recent spec from dialogue history.

        if prev spec was found, then:
            if action mentioned in curr spec request is 'close', then:
                remove prev spec from dialogue_history
        otherwise:
            cannot figure out prev spec so just inform user that the request is too ambiguous.

        recommend curr spec as the best action to take.
    '''

    @staticmethod
    def determine_best_action(context_window, state_tracker):
        # Step 1: context window must include a single request, otherwise end early.
        if not context_window.has_request:
            return

        # Step 2: extract setup + request from completed context window.
        request_utterance, request_gesture_target_id, request_dialogue_act, request_referring_expressions = \
            context_window.multimodal_data[-1]
        request_top_dialogue_act_label, request_bottom_dialogue_act_label = request_dialogue_act
        setup_utterances = context_window.utterances[:-1]

        # Step 3: top-level DA predicts request, otherwise end early.
        if request_top_dialogue_act_label != 'merged':
            return

        input_processing_rules_engine, \
        language_model_prediction_rules_engine, \
        established_reference_rules_engine, \
        discourse_rules_engine, \
        create_vis_not_from_existing_template_discourse_rules_engine, \
        create_vis_from_existing_template_discourse_rules_engine, \
        existing_vis_discourse_rules_engine = RuleEngineFactory.build()

        LanguageUnderstandingModels.K_CROSS_VALIDATION = -1
        LanguageUnderstandingModels.TOTAL_SUBJECTS = -1

        RuleContext.CURR_DIALOGUE_HISTORY = state_tracker
        RuleContext.USE_FULL_CONTEXT_WINDOW_FOR_DA_PREDICTION = context_window.use_full_context_window_for_da_prediction

        rule_context = RuleContext(context_window)
        rule_context = input_processing_rules_engine.execute(rule_context)
        rule_context = language_model_prediction_rules_engine.execute(rule_context)
        rule_context = established_reference_rules_engine.execute(rule_context)
        rule_context = discourse_rules_engine.execute(rule_context)
        rule_context = create_vis_not_from_existing_template_discourse_rules_engine.execute(rule_context)
        rule_context = create_vis_from_existing_template_discourse_rules_engine.execute(rule_context)
        rule_context = existing_vis_discourse_rules_engine.execute(rule_context)

        best_action = rule_context.curr_spec.spec

        if best_action:
            print(best_action.get_json_str())

        print("***HISTORY***\n")
        print(state_tracker)

    '''
    Algorithm flow:
        - The system has to make one of the following decisions once multimodal input is received:
            1. The speaker is not talking to the system.
                - Throw away such utterances. I.e., do not add to the context window.
            2. The speaker is talking to the system and it is a setup utterance.
                - Add to the context window. 
                - Now, keep listening for next utterance.
            3. The speaker is talking to the system and it is a request utterance.
                - Context window is complete (context window = setup + request).
                - Fork a new thread that determines best action to take.
            4. After request has been made, speaker is talking to the system.
                - Eventually a data attribute is mentioned which completes the conclusion part of contex window.
    '''

    def process_multimodal_input(self, utterance, gesture_target_id):
        # Step 1: tokenized the utterance which facilitates extraction of data attributes.
        tokenized_utterance = self.entity_tokenizer(utterance)
        # print("Tokenized utterance: "+str(tokenized_utterance))
        # Step 2: predict referring expressions
        referring_expressions = LanguageUnderstandingModels.predict_referring_expressions(tokenized_utterance)
        print("predicted referring expressions: {}".format([r.words for r in referring_expressions]))

        # Step 3: predict dialogue act
        context_utterances = [tokenized_utterance]
        dialogue_act = LanguageUnderstandingModels.predict_dialogue_act(
            context_utterances=context_utterances,
            gesture_target_id=gesture_target_id,
            referring_expressions=referring_expressions)
        print("predicted dialogue act: {}".format(dialogue_act))

        top_dialogue_act_label, bottom_dialogue_act_label = dialogue_act

        # Step 4: data attribute is mentioned while in conclusion state, clear the context and start fresh.
        if self.conclusion_mode and top_dialogue_act_label != 'merged':
            # print("In step 4")
            if tokenized_utterance._.entities:
                self.conclusion_mode = False

                del self.context_window
                self.context_window = ContextWindow()
            return

        # Step 5: otherwise our conversational state is one of the following:
        #   - conclusion mode: add utterance, context will get cleared in future once data attr is mentioned.
        #   - non-conclusion mode: add utterance, context will be completed once setup + request received.
        self.context_window.add(tokenized_utterance, gesture_target_id, dialogue_act, referring_expressions)

        # Step 6: if curr utterance is request, spawn new thread with completed context window (setup + request).
        if top_dialogue_act_label == 'merged':
            context_window_cpy = copy.deepcopy(self.context_window)
            self.context_window = ContextWindow()

            self.conclusion_mode = True
            self.found_data = False
            p = Process(target=
            SmarthubSession.determine_best_action(
                context_window=context_window_cpy,
                state_tracker=self.state_tracker))

            p.start()
            p.join()
            return

        # Step 7: data attribute is mentioned for first time since the last completed context window.
        # hence this is start of new context window.
        if not self.found_data and tokenized_utterance._.entities:
            found_data = True

            self.context_window = ContextWindow()
            self.context_window.add(tokenized_utterance, gesture_target_id, dialogue_act, referring_expressions)

    '''
    - The run() method is the starting point of a new Smarthub session. The general algorithm maintains the current 
    state of conversation. The states of conversation are:
        - speaker is not talking to Smarthub (i.e., no data attribute mentioned).
        - speaker is talking to Smarthub but no request has been made yet (setup state).
        - speaker is talking to Smarthub and request has been made (request state).
        - speaker is talking to Smarthub after request has been made (conclusion state).
    
    - Algorithm flow:
    While True:
        - Wait and listen for utterances and hand pointing gestures. 
        - Once utterance and hand pointing gesture is detected, process the multimodal input.
    '''

    # def run(self):
    #     while True:  # loop runs forever in current session
    #         utterance, gesture_target_id = FakeMultimodalService.listen()
    #         if (utterance == 'stop'or utterance == 'end conversation'):
    #             print("End of conversation")
    #             break
    #         else:
    #             print("Received multimodal input- utterance: {}, gesture target id: {}".
    #               format(utterance, gesture_target_id)) # utterance = FakeMultimodalService.listen()
    #             self.process_multimodal_input(utterance=utterance, gesture_target_id=gesture_target_id)
    #         # print("Received multimodal input- utterance: {}, gesture target id: {}".
    #         #       format(utterance))

    def run(self ):
        while True:  # loop runs forever in current session
            utterance, gesture_target_id = FakeMultimodalService.listen()
            # utterance, gesture_target_id = "show me a bar chart of County type", -1
            if (utterance == 'stop'or utterance == 'end conversation'):
                print("End of conversation")
                break
            else:
                print("Received multimodal input- utterance: {}, gesture target id: {}".
                  format(utterance, gesture_target_id)) # utterance = FakeMultimodalService.listen()
            # self.process_multimodal_input(utterance="can I see covid risk in the midwest", gesture_target_id=-1)
                self.process_multimodal_input(utterance=utterance, gesture_target_id=gesture_target_id)
            # self.process_multimodal_input(utterance="let's see", gesture_target_id=-1)
            # self.process_multimodal_input(utterance="what about for the southeast?", gesture_target_id=-1)

                # print("Received multimodal input- utterance: {}, gesture target id: {}".
                #   format(utterance))







# start a new Smarthub session:
smarthub = SmarthubSession()
smarthub.run()
