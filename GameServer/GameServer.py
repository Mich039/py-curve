import sched
import time
import random
from typing import Dict, Tuple
import math
import threading
from datetime import datetime
import logging

from GameObjects.Input.PlayerInput import PlayerInput
from GameObjects.LobbyState import LobbyState
from GameObjects.Player import Player
from GameObjects.Input.PlayerInput import PlayerInput
from GameObjects.PlayerStatus import PlayerStatus
from GameObjects.Point import Point
from GameServer.GameServerWrappers.GameStateWrapper import GameStateWrapper
from GameServer.GameServerWrappers.PlayerInputWrapper import PlayerInputWrapper
from GameServer.GameServerWrappers.PlayerWrapper import PlayerWrapper
import GameServer.ServerConstants as ServerConstants


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
        self._player_colors = {ServerConstants.PLAYER_COLORS[k]: None for k in range(8)}
        self._log.info("Created")

    def start(self):
        self._log.info("Server with id {id} has started".format(id=self.id))
        self._gameState.state = LobbyState.LOBBY
        self._scheduler.enter(delay=0, priority=0, action=self._tick)
        self._scheduler.run(blocking=True)

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
        new_payer.player.color = self._get_player_color(id)
        self._gameState.player_list[id] = new_payer
        self._broadcast_state()

    def receive_player_input(self, id: str, player_input: PlayerInput):
        if id not in self._inputs or self._inputs[id].timestamp < player_input.timestamp:
            self._inputs[id] = PlayerInputWrapper(player_input)
        else:
            print("Player with id: {id} sent outdated Input".format(id=id))

    def remove_player(self, id: str):
        self._gameState.remove(id)

    def _get_current_default_player_status(self) -> PlayerStatus:
        if self._gameState.state == LobbyState.IN_GAME:
            return PlayerStatus.SPECTATING
        else:
            return PlayerStatus.NOT_READY

    def _get_player_color(self, player_id: str):
        for k, v in self._player_colors.items():
            print(k, v)
            if self._player_colors[k] is None:
                print("free color found")
                self._player_colors[k] = player_id
                print("returning color")
                return k

    def _init_between_games(self):
        self._gameState.state = LobbyState.BETWEEN_GAMES
        for player in [player for player in self._gameState.player_list.values() if
                       not player.player.player_status == PlayerStatus.SPECTATING]:
            player.player.player_status = PlayerStatus.NOT_READY

    def _init_new_round(self):
        for player in [player for player in self._gameState.player_list.values() if
                       not player.player.player_status == PlayerStatus.SPECTATING]:
            player.player.player_status = PlayerStatus.ALIVE
            player.init_position(GameServer._get_random_point(), GameServer._get_random_angle())

    def _init_new_game(self):
        for player in self._gameState.player_list.values():
            player.reset_score()
        self._init_new_round()

    def _broadcast_state(self):
        if self._broadcast is not None:
            self._broadcast(self.id, self._gameState.to_game_state())

    def _tick(self):
        #print("ticking...")
        if not self._canceled:
            start_time = time.time()
            next_start_time = start_time + 1 / ServerConstants.TICK_RATE
            time_available = next_start_time*1000 - start_time*1000
            self._scheduler.enterabs(time=next_start_time, priority=0, action=self._tick)

        # React depending on State
        if self._gameState.state == LobbyState.IN_GAME:
            self._in_game_tick()
            time_taken = (time.time() * 1000 - start_time * 1000)
            print("Time taken: {time:.10f} ms {time_perc}%".format(time=time_taken,
                                                                   time_perc=time_taken / time_available))
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
        handle_result = self._handle_ready_inputs()
        if handle_result[1]:
            self._init_new_game()
            self._gameState.state = LobbyState.IN_GAME

        elif handle_result[0]:
            self._broadcast_state()
        #self._broadcast_state()

    def _players_alive(self) -> bool:
        """ Checks if more than one player is alive. True if so False if not """
        return len([player for player in self._gameState.player_list.values() if
                    player.player.player_status == PlayerStatus.ALIVE]) > 1

    def _calculate_score(self):
        for player_id, player in self._gameState.player_list.items():
            if player.player.player_status == PlayerStatus.ALIVE:
                player.player.score.score_points += ServerConstants.DEATH_SCORE

    def _in_game_tick(self):
        move_start_time = time.time() * 1000
        for player_id, player in self._gameState.player_list.items():
            if player.player.player_status == PlayerStatus.ALIVE:
                if not player.move(self._inputs[player_id], game_state=self._gameState):
                    player.player.player_status = PlayerStatus.DEAD
                    player.player.score.deaths += 1
                    self._calculate_score()
        print("Move took {t} ms".format(t=(time.time()*1000)-move_start_time))
        self._broadcast_state()

    def _handle_ready_inputs(self) -> Tuple[bool, bool]:
        """
        Handles the Ready Inputs for the States Lobby and Between Games.

        :returns
        A Tuple with two entries: The first one represents if a change happened.
        The second element is true if all players are ready
        """
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
            all_ready = all_ready and not player.player.player_status == PlayerStatus.NOT_READY
        return change, all_ready

    def _between_game_tick(self):
        handle_result = self._handle_ready_inputs()
        if handle_result[1]:
            self._init_new_round()
            self._gameState.state = LobbyState.IN_GAME

        elif handle_result[0]:
            self._broadcast_state()
