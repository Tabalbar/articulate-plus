from .data_augmentor import DataAugmentor
from ..corpus_extractor.extractor import Extractor


class Parser:
    @staticmethod
    def parse(corpus_path, corpus_entity_extractor, paraphraser=None, slot_replacer=None, \
              synonym_replacer=None, total_versions=10, process_refexps=False):
        corpus = Extractor.extract(corpus_path=corpus_path, utterance_cutoff=0, \
                                   process_refexps=process_refexps)
        for subject in corpus:
            subject_name = subject[0]
            contexts = list(subject[1])

            subject_context_components = dict()
            subject_context_components['subject_name'] = subject_name
            subject_context_components['contexts'] = []

            cnt = 0
            for context in contexts:
                print("Processing subject", subject_name, "with context", cnt, "out of", len(contexts))
                cnt += 1

                context_versions = DataAugmentor( \
                    corpus_entity_extractor=corpus_entity_extractor, paraphraser=paraphraser,
                    slot_replacer=slot_replacer, \
                    synonym_replacer=synonym_replacer, total_versions=total_versions)

                setup = context.get_setup()
                context_versions.add_context_component('setup', setup)

                request = context.get_request()
                context_versions.add_context_component('request', [request])

                conclusion = context.get_conclusion()
                context_versions.add_context_component('conclusion', conclusion)

                subject_context_components['contexts'].append(context_versions)

            yield subject_context_components
