from .node import Node
from .parsed_dependency import ParsedDependency


class DependencyParser:
    @staticmethod
    def parse(doc):
        parsed_dependencies = []

        for sent in doc.sents:
            root_token = sent.root
            root = Node(data=(root_token, root_token.text, \
                              root_token.tag_, root_token.pos_, root_token.lemma_, root_token.dep_))
            DependencyParser.rec_parse(parent=root)
            parsed_dependencies.append(ParsedDependency(parsed_dependency=root, sentence=sent))

        return parsed_dependencies

    @staticmethod
    def rec_parse(parent):
        # parent_token = parent.get_data()[0]

        if parent is None:
            parent.set_is_leaf(True)
            return

        parent_token = parent.get_data()[0]

        for child_token in parent_token.children:
            child = Node(data=(child_token, child_token.text, \
                               child_token.tag_, child_token.pos_, child_token.lemma_, child_token.dep_))
            parent.add_child(child)
            DependencyParser.rec_parse(parent=child)

    @staticmethod
    def json_tree_parse(doc):
        parsed_dependencies = []
        dependency_parse = doc.print_tree(light=False)

        for data in dependency_parse:
            word = data['word']
            pos_fine = data['POS_fine']
            pos_coarse = data['POS_coarse']
            arc = data['arc']

            lemma = None
            if 'lemma' in data:
                lemma = data['lemma']

            modifiers = data['modifiers']

            root = Node(data=(word, pos_fine, pos_coarse, lemma, arc, modifiers))
            DependencyParser.rec_parse(parent=root)
            parsed_dependencies.append(ParsedDependency(parsed_dependency=root))

        return parsed_dependencies

    @staticmethod
    def json_tree_rec_parse(parent):
        parent_modifiers = parent.get_data()[5]
        if len(parent_modifiers) == 0:
            parent.set_is_leaf(True)
            return

        for data in parent_modifiers:
            word = data['word']
            pos_fine = data['POS_fine']
            pos_coarse = data['POS_coarse']
            arc = data['arc']

            lemma = None
            if 'lemma' in data:
                lemma = data['lemma']

            child_modifiers = data['modifiers']

            child = Node(data=(word, pos_fine, pos_coarse, lemma, arc, child_modifiers))

            parent.add_child(child)

            DependencyParser.rec_parse(parent=child)
