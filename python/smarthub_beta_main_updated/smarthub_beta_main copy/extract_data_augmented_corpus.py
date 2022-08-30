from dev.corpus_data_augmentor.utils import Utils
from dev.corpus_extractor.extractor import Extractor

print("Started iterating extracted data...")

augment_with_paraphrases = True
augment_with_slot_replacement = True
augment_with_synonym_replacement = False
total_versions = 10

corpus_path = Utils.get_corpus_path(
    augment_with_paraphrases=augment_with_paraphrases,
    augment_with_slot_replacement=augment_with_slot_replacement,
    augment_with_synonym_replacement=augment_with_synonym_replacement,
    total_versions=total_versions)

data = Extractor.extract_from_json(corpus_path=corpus_path, process_refexps=False)
for subject in data:
    subject_name = subject[0]
    contexts = subject[1]
    print("\n************SUBJECT NAME " + subject_name + " *************\n")
    for context in contexts:
        setup = context.get_setup()
        request = context.get_request()
        conclusion = context.get_conclusion()

        print("SETUP", [s.get_context_component_as_json() for s in setup])
        print("REQUEST", request.get_context_component_as_json())
        print("CONCLUSION", [s.get_context_component_as_json() for s in conclusion])

print("Completed iterating extracted data...")
