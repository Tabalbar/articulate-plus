class TextSpan:
    def __init__(self, span, matching_token):
        self.span = span
        self.matching_token = matching_token

    def get_span(self):
        return self.span

    def get_start(self):
        return self.span[0]

    def get_end(self):
        span = self.get_span()
        return span[len(span) - 1] + 1

    def get_matching_token(self):
        return self.matching_token

    def __hash__(self):
        return hash((self.get_span(),))

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.get_span() == other.get_span()

    def __str__(self):
        return self.get_span()
