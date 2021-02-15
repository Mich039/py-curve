import GameObjects.Player as Player

class PlayerWrapper:

    def __init__(self, player: Player):
        self._player: Player = player
        self._invisible_since: int = 0
        self._is_alive: bool = False
        self._velocity: float = 1.0

    @property
    def player(self) -> Player:
        return self._player

    @player.setter
    def player(self, value: Player):
        self._player = value

    @property
    def invisible_since(self) -> int:
        return self._invisible_since

    @invisible_since.setter
    def invisible_since(self, value: int):
        self._invisible_since = value

    @property
    def is_alive(self) -> bool:
        return self._is_alive

    @is_alive.setter
    def is_alive(self, value: bool):
        self._is_alive = value

    @property
    def velocity(self) -> float:
        return self._velocity

    @velocity.setter
    def velocity(self, value: float):
        self._velocity = value
