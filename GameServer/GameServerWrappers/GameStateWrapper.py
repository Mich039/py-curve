from typing import List, Dict

from GameObjects.GameState import GameState
from GameObjects.LobbyState import LobbyState
from GameObjects.PowerUp import PowerUp
from GameServer.GameServerWrappers.PlayerWrapper import PlayerWrapper

class GameStateWrapper:

    def __init__(self, id):
        self._player_list: Dict[str, PlayerWrapper] = dict()
        self._to_remove: List[str] = []
        self._ground_power_up = []
        self._state: LobbyState = LobbyState.LOBBY
        self._game_server_id = id

    @property
    def game_server_id(self):
        return self._game_server_id

    @game_server_id.setter
    def game_server_id(self, value):
        self._game_server_id = value

    @property
    def player_list(self) -> Dict[str, PlayerWrapper]:
        return self._player_list

    @player_list.setter
    def player_list(self, value: Dict[str, PlayerWrapper]):
        self._player_list = value

    @property
    def to_remove(self) -> List[str]:
        return self._to_remove

    @to_remove.setter
    def to_remove(self, value: List[str]):
        self._to_remove = value

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

    def remove(self, id: str):
        self._to_remove.append(id)

    def to_game_state(self) -> GameState:
        game_state = GameState()
        game_state.player_list = [v.get_wrapped_player() for k, v in self._player_list.items()]
        game_state.state = self._state
        game_state.game_server_id = self._game_server_id
        game_state.ground_power_up = self._ground_power_up
        return game_state
