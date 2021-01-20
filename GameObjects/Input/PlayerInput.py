from datetime import datetime


class PlayerInput:

    def __init__(self):
        self._left = False
        self._right = False
        self._space = False
        self._timestamp = datetime.now()
        
    @property
    def timestamp(self) -> datetime:
        return self._timestamp
    
    @timestamp.setter
    def timestamp(self, value: datetime):
        self._timestamp = value

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
