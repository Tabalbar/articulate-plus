class Entity:
    def __init__(self, name, value, data_attribute):
        self.name = name
        self.data_attribute = data_attribute
        self.value = value
        self.is_regular_expression = False
        self.synonyms = set()
        self.hyponyms = set()
        self.is_named_entity_category = False

        if value is None:
            self.is_named_entity_category = True
            return

        self.is_regular_expression = False

    def get_name(self):
        return self.name

    def get_value(self):
        return self.value

    def add_synonyms(self, synonyms):
        self.synonyms.update(synonyms)

    def get_synonyms(self):
        if not self.synonyms:
            return None
        if len(self.synonyms) == 0:
            return None
        return list(self.synonyms)

    def get_hyponyms(self):
        if not self.hyponyms:
            return None
        if len(self.hyponyms) == 0:
            return None
        return list(self.hyponyms)

    def add_hyponyms(self, hyponyms):
        self.hyponyms.update(hyponyms)

    def get_data_attribute(self):
        return self.data_attribute

    def get_is_regular_expression(self):
        return self.is_regular_expression

    def set_is_regular_expression(self, is_regular_expression):
        self.is_regular_expression = is_regular_expression

    def get_is_named_entity_category(self):
        return self.is_named_entity_category
