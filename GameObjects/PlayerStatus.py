import enum


class PlayerStatus(enum.Enum):
    ALIVE = enum.auto()
    DEAD = enum.auto()
    READY = enum.auto()
    NOT_READY = enum.auto()
    SPECTATING = enum.auto()
