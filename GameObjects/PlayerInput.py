class PlayerInput:

    def __init__(self):
        self._left = False
        self._right = False
        self._space = False

    @property
    def left(self):
        """Property left"""
        return self._left

    @left.setter
    def left(self, value):
        self._left = value

    @property
    def right(self):
        return self._right

    @right.setter
    def right(self, value):
        self._right = value

    @property
    def space(self):
        return self._space

    @space.setter
    def space(self, value):
        self._space = value
