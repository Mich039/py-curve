class PlayerInput:

    def __init__(self):
        self._left = False
        self._right = False
        self._space = False

    @property
    def left(self) -> bool:
        """Property left"""
        return self._left

    @left.setter
    def left(self, value: bool):
        self._left = value

    @property
    def right(self) -> bool:
        return self._right

    @right.setter
    def right(self, value: bool):
        self._right = value

    @property
    def space(self) -> bool:
        return self._space

    @space.setter
    def space(self, value: bool):
        self._space = value
