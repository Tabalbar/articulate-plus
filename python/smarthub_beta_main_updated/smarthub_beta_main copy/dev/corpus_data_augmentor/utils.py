from ..corpus_extractor.corpus_extraction_paths import CorpusExtractionPaths


class Utils:
    @staticmethod
    def get_corpus_path(
            augment_with_paraphrases=False,
            augment_with_slot_replacement=False,
            augment_with_synonym_replacement=False,
            total_versions=10):

        if not augment_with_paraphrases and not \
                augment_with_slot_replacement and not \
                augment_with_synonym_replacement:
            corpus_path = CorpusExtractionPaths.JSON_CORPUS_DATA
            return corpus_path

        corpus_path = CorpusExtractionPaths.AUGMENTED_CORPUS_DATA[:-1 * len('.json')] \
                      + '_' + str(total_versions)

        if augment_with_paraphrases:
            corpus_path += '_par'

        if augment_with_slot_replacement:
            corpus_path += '_slot'

        if augment_with_synonym_replacement:
            corpus_path += '_syn'

        return corpus_path + '.json'
