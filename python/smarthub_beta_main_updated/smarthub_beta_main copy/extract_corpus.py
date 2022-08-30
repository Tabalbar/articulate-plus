from dev.corpus_data_augmentor.utils import Utils
from dev.corpus_extractor.extractor import Extractor

corpus_path = Utils.get_corpus_path(
    augment_with_paraphrases=False,
    augment_with_slot_replacement=False,
    augment_with_synonym_replacement=False)

print("Started iterating corpus from ", corpus_path)
data = Extractor.extract(corpus_path=corpus_path)

sum_context_utterances_size = 0
max_context_utterances_size = 0
total_contexts = 0
total_before_after = 0
for subject in data:
    subject_name = subject[0]
    contexts = subject[1]
    print("\n************SUBJECT NAME " + subject_name + " *************\n")
    for context in contexts:
        setup = context.get_setup()
        request = context.get_request()
        conclusion = context.get_conclusion()

        setup_utts = [s.get_context_component_as_json()['utterance'][3] for s in setup]
        request_utt = request.get_context_component_as_json()['utterance'][3]
        conc_utts = [s.get_context_component_as_json()['utterance'][3] for s in conclusion]

        total_length = len(setup_utts) + 1 + len(conc_utts)
        if total_length > 1:
            total_before_after += 2 * total_length - 2
        else:
            total_before_after += 1

        [print(utt + '\n') for utt in setup_utts]
        print(request_utt + '\n')
        [print(utt + '\n') for utt in conc_utts]

        context_utterances_size = len(setup_utts) + 1 + len(conc_utts)
        print("TOTAL utterances in context", context_utterances_size)

        if context_utterances_size > max_context_utterances_size:
            max_context_utterances_size = context_utterances_size
        sum_context_utterances_size += context_utterances_size
        total_contexts += 1
print("total_before_after", total_before_after)
print("Completed iterating extracted data...")
print("Max context utterances size", max_context_utterances_size)
print("Avg context utterances size", float(sum_context_utterances_size) / total_contexts)
