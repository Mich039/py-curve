import enum


class LobbyState(enum.Enum):
    LOBBY = enum.auto()
    IN_GAME = enum.auto()
    BETWEEN_GAMES = enum.auto()
