from typing import List

from GameObjects.LobbyState import LobbyState
from GameObjects.Player import Player
from GameObjects.PowerUp import PowerUp


class GameState:

    def __init__(self):
        self._player_list = None
        self._ground_power_up = None
        self._state = None

    @property
    def player_list(self) -> List[Player]:
        return self._player_list

    @player_list.setter
    def player_list(self, value: List[Player]):
        self._player_list = value

    @property
    def ground_power_up(self) -> List[PowerUp]:
        return self._ground_power_up

    @ground_power_up.setter
    def ground_power_up(self, value: List[PowerUp]):
        self._ground_power_up = value

    @property
    def state(self) -> LobbyState:
        return self._state

    @state.setter
    def state(self, value: LobbyState):
        self._state = value
