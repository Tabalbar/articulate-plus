class Level:
    def __init__(self, top_level_info=None, bottom_level_info=None):
        self._data = [top_level_info, bottom_level_info]

    def get_top_level(self):
        return self._data[0]

    def get_bottom_level(self):
        return self._data[1]

    def set_top_level(self, top_level_info):
        self._data[0] = top_level_info

    def set_bottom_level(self, bottom_level_info):
        self._data[1] = bottom_level_info

    def exists(self):
        return self._data[0] or self._data[1]
