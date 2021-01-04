from typing import List

from GameObjects.Color import Color
from GameObjects.PlayerStatus import PlayerStatus
from GameObjects.Point import Point
from GameObjects.PowerUp import PowerUp
from GameObjects.Score import Score


class Player:

    def __init__(self):
        self._name = None
        self._player_status = None
        self._color = None
        self._head = None
        self._body = None
        self._active_power_ups = None
        self._score = None

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    @property
    def player_status(self) -> PlayerStatus:
        return self._player_status

    @player_status.setter
    def player_status(self, value: PlayerStatus):
        self._player_status = value

    @property
    def color(self) -> Color:
        return self._color

    @color.setter
    def color(self, value: Color):
        self._color = value

    @property
    def head(self) -> Point:
        return self._head

    @head.setter
    def head(self, value: Point):
        self._head = value

    @property
    def body(self) -> List[List[Point]]:
        return self._body

    @body.setter
    def body(self, value: List[List[Point]]):
        self._body = value

    @property
    def active_power_ups(self) -> List[PowerUp]:
        return self._active_power_ups

    @active_power_ups.setter
    def active_power_ups(self, value: List[PowerUp]):
        self._active_power_ups = value

    @property
    def score(self) -> Score:
        return self._score

    @score.setter
    def score(self, value: Score):
        self._score = value
