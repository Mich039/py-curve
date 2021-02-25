import enum


class PowerUpType(enum.Enum):
    SPEED = enum.auto()
    SLOW = enum.auto()
    FLYING = enum.auto()
    CLEAR = enum.auto()
    ENEMY_INVERSE = enum.auto()
    CORNER = enum.auto()
    ENEMY_CORNER = enum.auto()
