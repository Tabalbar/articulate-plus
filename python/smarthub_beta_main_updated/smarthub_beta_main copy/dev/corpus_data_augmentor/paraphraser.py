import json
from .data_augmentor_paths import DataAugmentorPaths


class Paraphraser:
    def __init__(self, paraphrases_json_path=DataAugmentorPaths.PARAPHRASES_DIR):
        with open(paraphrases_json_path, 'r') as f:
            self.paraphrases = json.load(f)

    def get_paraphrases(self, utterance, number_of_paraphrases=20):
        return self.paraphrases[utterance][:number_of_paraphrases]
