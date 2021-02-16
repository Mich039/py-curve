from datetime import datetime

from GameObjects.Input.PlayerInput import PlayerInput


class PlayerInputWrapper:

    def __init__(self, player_input: PlayerInput):
        self._left: bool = player_input.left
        self._right: bool = player_input.right
        self._space: bool = player_input.space
        self._processed: bool = False
        self._timestamp: datetime = player_input.timestamp

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

    @property
    def processed(self) -> bool:
        return self._processed

    @processed.setter
    def processed(self, value: bool):
        self._processed = value