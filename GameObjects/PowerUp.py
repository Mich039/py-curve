from GameObjects.Point import Point
from GameObjects.PowerUpType import PowerUpType


class PowerUp:

    def __init__(self):
        self._power_up_type = None
        self._total_ticks = None
        self._ticks_left = None
        self._location = None

    @property
    def power_up_type(self) -> PowerUpType:
        return self._power_up_type

    @power_up_type.setter
    def power_up_type(self, value: PowerUpType):
        self._power_up_type = value

    @property
    def total_ticks(self) -> int:
        return self._total_ticks

    @total_ticks.setter
    def total_ticks(self, value: int):
        self._total_ticks = value

    @property
    def ticks_left(self) -> int:
        return self._ticks_left

    @ticks_left.setter
    def ticks_left(self, value: int):
        self._ticks_left = value

    @property
    def location(self) -> Point:
        return self._location

    @location.setter
    def location(self, value: Point):
        self._location = value
