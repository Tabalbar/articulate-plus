import sys


class ParsedDependency:
    def __init__(self, parsed_dependency, sentence):
        self.parsed_dependency = parsed_dependency
        self.sentence = sentence

    def get_parsed_dependency(self):
        return self.parsed_dependency

    def traverse(self):
        return self.rec_traverse( \
            parent=self.get_parsed_dependency())

    def rec_traverse(self, parent):
        elements = []

        data = parent.get_data()
        elements.append((data[0], data[1], data[2], data[3], data[4], data[5]))

        if parent.get_is_leaf():
            return elements

        for child in parent.get_children():
            elements += self.rec_traverse(parent=child)

        return elements

    def print(self):
        print(self.get_parsed_dependency())

    def pretty_print(self):
        def __showTree(token, level):
            tab = "\t" * level
            sys.stdout.write("\n%s{" % (tab))
            [__showTree(t, level + 1) for t in token.lefts]
            sys.stdout.write("\n%s\t%s [%s] (%s)" % (tab, token, token.dep_, token.tag_))
            [__showTree(t, level + 1) for t in token.rights]
            sys.stdout.write("\n%s}" % (tab))

        return __showTree(self.sentence.root, 1)

    def get_phrases(self, pos='ADP'):
        return self.rec_get_phrases( \
            parent=self.get_parsed_dependency(), pos=pos)

    def rec_get_phrases(self, parent, pos):
        elements = []

        data = parent.get_data()
        if data[3] == pos:
            elements.append(self.rec_traverse(parent=parent))

        if parent.get_is_leaf():
            return elements

        for child in parent.get_children():
            elements += self.rec_get_phrases(parent=child, pos=pos)

        return elements
