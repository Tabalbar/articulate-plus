from abc import ABC, abstractmethod


class Rule(ABC):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def execute(self, rule_context):
        raise NotImplementedError()

    @abstractmethod
    def should_execute(self, rule_context):
        raise NotImplementedError()
