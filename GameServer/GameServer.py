import logging
import math
import threading
from datetime import datetime
from typing import Dict

import random
import sched, time
from GameObjects.LobbyState import LobbyState
from GameObjects.Player import Player
from GameObjects.Input.PlayerInput import PlayerInput
from GameObjects.PlayerStatus import PlayerStatus
from GameServer.GameServerWrappers.GameStateWrapper import GameStateWrapper
from GameServer.GameServerWrappers.PlayerInputWrapper import PlayerInputWrapper
from GameServer.GameServerWrappers.PlayerWrapper import PlayerWrapper

PLAY_AREA_SIZE = 1000
TICK_RATE = 1.0
BASE_SPEED = 1.0
player_states: Dict[Player, PlayerInput] = dict()
player_ticks_to_next_hole: Dict[Player, int] = dict()
player_hole_ticks_left: Dict[Player, int] = dict()


class GameServer:
    # Add, input, remove
    def __init__(self, id: int):
        self._log = logging.getLogger('GameServer {0}'.format(id))
        self._id = id
        self._gameState: GameStateWrapper = GameStateWrapper()
        self._broadcast = None
        self._inputs: Dict[str, PlayerInputWrapper] = dict()
        self._scheduler: sched.scheduler = sched.scheduler(time.time, time.sleep)
        self._canceled: bool = False
        self._log.info("Created")

    def start(self):
        self._log.info("Server with id {id} has started".format(id=self.id))
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

    def add_player(self, id: str):
        self._log.info("Add player with id {0}".format(id))
        new_payer = PlayerWrapper(Player(id))
        new_payer.player.player_status = self._get_current_default_player_status()
        self._gameState.player_list[id] = new_payer
        self._broadcast_state()

    def receive_player_input(self, id: str, player_input: PlayerInput):
        self._inputs[id] = PlayerInputWrapper(player_input)
        # TODO: Check for the Timestamp

    def remove_player(self, id: str):
        self._gameState.remove(id)

    def _get_current_default_player_status(self) -> PlayerStatus:
        if self._gameState.state == LobbyState.IN_GAME:
            return PlayerStatus.SPECTATING
        else:
            return PlayerStatus.NOT_READY

    def _init_new_round(self):
        pass

    def _init_new_game(self):
        pass

    def _broadcast_state(self):
        if self._broadcast is not None:
            self._broadcast(self.id, self._gameState.to_game_state())

    def _tick(self):
        if not self._canceled:
            self._scheduler.enterabs(time=time.time() + 1 / TICK_RATE, priority=0, action=self._tick)

        # React depending on State
        if self._gameState.state == LobbyState.IN_GAME:
            self._in_game_tick()
        elif self._gameState.state == LobbyState.BETWEEN_GAMES:
            self._between_game_tick()
        else:
            self._lobby_tick()

        self._inputs_processed()

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
        for k in player_ticks_to_next_hole.keys():
            player_ticks_to_next_hole[k] -= 1
        for k in player_hole_ticks_left.keys():
            player_hole_ticks_left[k] -= 1
        self.move()

    def _between_game_tick(self):
        pass