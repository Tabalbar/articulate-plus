import glob
import json
import os

from .parser import Parser


class Extractor:
    @staticmethod
    def get_file_paths(corpus_path):
        for file_path in glob.glob(corpus_path + '*.json'):
            yield file_path

    @staticmethod
    def get_subject(file_path, utterance_cutoff=4, process_refexps=True):
        path_parts = file_path.split('/')
        subject_name = os.path.basename(file_path)[:-len('.json')]
        return subject_name, Parser.parse(file_path=file_path, utterance_cutoff=utterance_cutoff,
                                          process_refexps=process_refexps)

    @staticmethod
    def extract(corpus_path, utterance_cutoff=4, process_refexps=True):
        for file_path in Extractor.get_file_paths(corpus_path=corpus_path):
            subject_name, subject_contexts = Extractor.get_subject(file_path,
                                                                   utterance_cutoff=utterance_cutoff,
                                                                   process_refexps=process_refexps)
            print("Completed processing subject", subject_name)
            yield subject_name, subject_contexts

    @staticmethod
    def get_subject_from_json(subject_json, process_refexps=True):
        return subject_json['subject_name'], Parser.parse_from_json(subject_json=subject_json['contexts'],
                                                                    process_refexps=process_refexps)

    @staticmethod
    def extract_from_json(corpus_path, total_versions=50, process_refexps=True):
        with open(corpus_path, 'r') as f:
            subjects = json.load(f)

        for subject in subjects:
            if int(subject['subject_name'].split('_')[1]) >= total_versions:
                continue

            subject_name, subject_contexts = Extractor.get_subject_from_json(subject_json=subject,
                                                                             process_refexps=process_refexps)
            print("Completed processing subject", subject_name)
            yield subject_name, subject_contexts
