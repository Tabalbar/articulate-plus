class ReferringExpressionInfo:
    def __init__(self):
        self.word_indices = []

        self.start_char_indices = []
        self.end_char_indices = []

        self.words = []

        self.labels = []

        self.word_offset = 0

        self.char_offset = 0

        self.rid = None

        self.targets = None

        self.properties = None

    def add(self, word_idx, start_char_idx, end_char_idx, word, label):
        self.word_indices.append(word_idx)
        self.start_char_indices.append(start_char_idx)
        self.end_char_indices.append(end_char_idx)
        self.words.append(word)
        self.labels.append(label)

        if start_char_idx:
            self.char_offset += end_char_idx - start_char_idx + 1

        self.word_offset += 1

    def get_start_word_idx(self):
        return self.word_indices[0]

    def get_end_word_idx(self):
        return self.word_indices[-1]

    def get_start_char_idx(self):
        return self.start_char_indices[0]

    def get_end_char_idx(self):
        return self.end_char_indices[-1]

    def get_info(self):
        info = []
        for word_idx, start_char_idx, end_char_idx, \
            word, label in zip(
            self.word_indices, self.start_char_indices, self.end_char_indices,
            self.words, self.labels):
            info.append((word_idx, start_char_idx, end_char_idx, word, label))
        return self.rid, self.targets, self.properties, info

    def __str__(self):
        s = ''
        for word_idx, start_char_idx, end_char_idx, word, label in \
                zip(self.word_indices, self.start_char_indices, self.end_char_indices, self.words, self.labels):
            # s += '(WordIdx ' + str(word_idx) + ', StartCharIdx ' + str(start_char_idx) + ', EndCharIdx ' + str(
            #    end_char_idx) + \
            #     ', Word ' + word + ', Label ' + label + '), '
            s += '(Word ' + word + ', Label ' + label + '), '
        s = s if s else str(None)
        return 'RefId ' + str(self.rid) + ', Targets ' + str(self.targets) + ', Properties ' + str(self.properties) +\
               ', Info ' + s
