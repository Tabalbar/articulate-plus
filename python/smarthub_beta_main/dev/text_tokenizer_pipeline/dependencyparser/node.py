class Node:
    def __init__(self, data):
        self.children = []
        self.parent = None
        self.is_leaf = False
        self.data = data

    def add_child(self, child):
        child.set_parent(self)
        self.children.append(child)
        return child

    def get_children(self):
        return self.children

    def get_data(self):
        return self.data

    def set_data(self, data):
        self.data = data

    def set_parent(self, parent):
        self.parent = parent

    def set_is_leaf(self, is_leaf):
        self.is_leaf = is_leaf

    def get_is_leaf(self):
        return self.is_leaf

    def __str__(self):
        s = self.rec_str(parent=self)
        return s

    def rec_str(self, parent):
        s = ''

        data = parent.get_data()
        s += str(data[0:len(data)]) + '\n'

        if parent.get_is_leaf():
            return s

        for child in parent.get_children():
            s += self.rec_str(parent=child)

        return s
