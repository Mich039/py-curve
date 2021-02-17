import sched
import time
import random
from typing import Dict

from GameObjects.Input.PlayerInput import PlayerInput
from GameObjects.LobbyState import LobbyState
from GameObjects.Player import Player
from GameObjects.PlayerStatus import PlayerStatus
from GameObjects.Point import Point
from GameServer.GameServerWrappers.GameStateWrapper import GameStateWrapper
from GameServer.GameServerWrappers.PlayerInputWrapper import PlayerInputWrapper
from GameServer.GameServerWrappers.PlayerWrapper import PlayerWrapper
import GameServer.ServerConstants as ServerConstants


class GameServer:
    # Add, input, remove
    def __init__(self, id: int):
        self._id = id
        self._gameState: GameStateWrapper = GameStateWrapper()
        self._broadcast = None
        self._inputs: Dict[int, PlayerInputWrapper] = dict()
        self._scheduler: sched.scheduler = sched.scheduler(time.time, time.sleep)
        self._canceled: bool = False

    def start(self):
        print("Server with id {id} has started".format(id=self.id))
        self._gameState.state = LobbyState.LOBBY
        self._scheduler.enter(delay=0, priority=0, action=self._tick)
        self._scheduler.run()

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    @property
    def broadcast(self):
        return self._broadcast

    @broadcast.setter
    def broadcast(self, value):
        self._broadcast = value

    def add_player(self, id: int):
        new_payer = PlayerWrapper(Player(id))
        new_payer.player.player_status = self._get_current_default_player_status()
        self._gameState.player_list[id] = new_payer

    def receive_player_input(self, id: int, player_input: PlayerInput):
        if id not in self._inputs or self._inputs[id].timestamp < player_input.timestamp:
            self._inputs[id] = PlayerInputWrapper(player_input)
        else:
            print("Player with id: {id} sent outdated Input".format(id=id))

    def remove_player(self, id: int):
        self._gameState.remove(id)

    def _get_current_default_player_status(self) -> PlayerStatus:
        if self._gameState.state == LobbyState.IN_GAME:
            return PlayerStatus.SPECTATING
        else:
            return PlayerStatus.NOT_READY

    def _init_new_round(self):
        for player in self._gameState.player_list.values():
            player.init_position(GameServer._get_random_point(), GameServer._get_random_angle())

    def _init_new_game(self):
        for player in self._gameState.player_list.values():
            player.reset_score()
        self._init_new_round()

    def _broadcast_state(self):
        if self._broadcast is not None:
            self._broadcast(self.id, self._gameState.to_game_state())

    def _tick(self):
        if not self._canceled:
            self._scheduler.enterabs(time=time.time() + 1 / ServerConstants.TICK_RATE, priority=0, action=self._tick)

        # React depending on State
        if self._gameState.state == LobbyState.IN_GAME:
            self._in_game_tick()
        elif self._gameState.state == LobbyState.BETWEEN_GAMES:
            self._between_game_tick()
        else:
            self._lobby_tick()

        self._inputs_processed()

    @staticmethod
    def _get_random_angle() -> float:
        return random.uniform(0, 360)

    @staticmethod
    def _get_random_point() -> Point:
        return Point(random.uniform(0, ServerConstants.PLAY_AREA_SIZE),
                     random.uniform(0, ServerConstants.PLAY_AREA_SIZE))

    def _inputs_processed(self):
        for input in self._inputs.values():
            input.processed = True

    def _lobby_tick(self):
        # Process Inputs
        change: bool = False
        for key, value in self._inputs.items():
            if value.space and not value.processed:
                old_state = self._gameState.player_list[key].player.player_status
                self._gameState.player_list[key].player.player_status = \
                    PlayerStatus.READY if old_state == PlayerStatus.NOT_READY else PlayerStatus.NOT_READY
                change = True

        # Check if all Players are ready
        all_ready: bool = len(self._gameState.player_list) > 0
        for player_id, player in self._gameState.player_list.items():
            all_ready = all_ready and player.player.player_status == PlayerStatus.READY

        if all_ready:
            self._init_new_game()
            self._gameState.state = LobbyState.IN_GAME

        elif change:
            self._broadcast_state()

    def _in_game_tick(self):
        for player_id, player in self._gameState.player_list.items():
            if player.is_alive:
                player.is_alive = player.move(self._inputs[player_id], game_state=self._gameState)
                # TODO: Calculate Score if a player dies
        self._broadcast_state()
    def _between_game_tick(self):
        pass
