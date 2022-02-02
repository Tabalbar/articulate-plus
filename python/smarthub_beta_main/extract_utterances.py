from dev.corpus_extractor.corpus_extraction_paths import CorpusExtractionPaths
from dev.corpus_extractor.extractor import Extractor
from dev.corpus_data_augmentor.data_augmentor_paths import DataAugmentorPaths

print("Started iterating extracted data...")
paraphrases = dict()

utterance_cutoff = 0

data = Extractor.extract(corpus_path=CorpusExtractionPaths.JSON_CORPUS_DATA, utterance_cutoff=utterance_cutoff)
for subject in data:
    subject_name = subject[0]
    contexts = subject[1]

    print("\n************SUBJECT NAME " + subject_name + " *************\n")
    for context in contexts:
        setup = context.get_setup()
        request = context.get_request()
        conclusion = context.get_conclusion()

        setup_context_components = [ \
            s.get_context_component_as_json() \
                ['utterance'][3] for s in setup]

        for setup_context_component in setup_context_components:
            if len(setup_context_component.split()) < utterance_cutoff:
                print("SKIPPING", setup_context_component)
                continue
            print(setup_context_component)
            paraphrases[setup_context_component] = setup_context_component
            with open(DataAugmentorPaths.UTTERANCES_DIR, 'a+') as f:
                f.write(setup_context_component)
                f.write(';\n')

        request_context_components = [request.get_context_component_as_json() \
                                          ['utterance'][3]]

        for request_context_component in request_context_components:
            if len(request_context_component.split()) < utterance_cutoff:
                print("SKIPPING", request_context_component)
                continue
            print(request_context_component)
            paraphrases[request_context_component] = request_context_component
            with open(DataAugmentorPaths.UTTERANCES_DIR, 'a+') as f:
                f.write(request_context_component)
                f.write(';\n')

        conclusion_context_components = [ \
            s.get_context_component_as_json() \
                ['utterance'][3] for s in conclusion]

        for conclusion_context_component in conclusion_context_components:
            if len(conclusion_context_component.split()) < utterance_cutoff:
                print("SKIPPING", conclusion_context_component)
                continue
            print(conclusion_context_component)
            paraphrases[conclusion_context_component] = conclusion_context_component
            with open(DataAugmentorPaths.UTTERANCES_DIR, 'a+') as f:
                f.write(conclusion_context_component)
                f.write(';\n')

print("Completed iterating extracted data...")
