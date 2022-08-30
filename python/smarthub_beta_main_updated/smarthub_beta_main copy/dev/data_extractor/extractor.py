import abc
from abc import ABCMeta


class Extractor(metaclass=ABCMeta):
    __metaclass__ = abc.ABCMeta

    def __init__(self, input_source_file, output_target_file, base_url):
        self.input_source_file = input_source_file
        self.output_target_file = output_target_file
        self.base_url = base_url
        self.entities = []

    @abc.abstractmethod
    def extract(self):
        pass

    def get_base_url(self):
        return self.base_url

    def get_entities(self):
        return self.entities
