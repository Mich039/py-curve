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

TICK_RATE = 1.0
BASE_SPEED = 1.0
player_states: Dict[Player, PlayerInput] = dict()
player_ticks_to_next_hole: Dict[Player, int] = dict()
player_hole_ticks_left: Dict[Player, int] = dict()


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
        print("Server has started")
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
        self._inputs[id] = PlayerInputWrapper(player_input)
        # TODO: Check for the Timestamp

    def remove_player(self, id: int):
        self._gameState.remove(id)

    def is_visible(self, player: Player):
        if player_hole_ticks_left.get(player, 0) > 0:
            return False
        return True

    def create_hole_for(self, player: Player):
        pass
        # player.body.append([])
        # if is_visible(player):
        #     tick_length = random.random(50, 200)
        #     player_hole_ticks_left[player] = tick_length

    def rotate_by(self, player: Player, angle: int):
        Player.angle += math.radians(angle)
        # print(f"xVorher: {self.x}")
        # x = math.sin(angle)
        # print(f"xAfter: {self.x}")
        # y = -math.cos(angle)

    def move(self, player: Player, player_input: PlayerInput):
        if player_input.left:
            self.rotate_by(player, -5)

        if player_input.right:
            self.rotate_by(player, 5)

        player.head.x += BASE_SPEED * math.sin(player.angle)
        player.head.y += BASE_SPEED * -math.cos(player.angle)

        # self.point = (self.posX, self.posY)

        if self.is_visible(player):
            if len(player.body) == 0:
                player.body.append([])

            player.body[len(player.body) - 1].append((player.head.x, player.head.y))
            if random.random() < 0.005:
                player.invisible_since = datetime.now()
                player.body.append(player.curr_line)
                player.curr_line = []

    def _get_current_default_player_status(self) -> PlayerStatus:
        if self._gameState.state == LobbyState.IN_GAME:
            return PlayerStatus.SPECTATING
        else:
            return PlayerStatus.NOT_READY

    def _broadcast_state(self):
        if self._broadcast is not None:
            self._broadcast(self._gameState.to_game_state())

    def _tick(self):
        if not self._canceled:
            self._scheduler.enterabs(time=time.time() + 1 / TICK_RATE, priority=0, action=self._tick)

        # React depending on State
        if self._gameState.state == LobbyState.IN_GAME:
            self._in_game_tick()
        elif self._gameState.state == LobbyState.IN_GAME:
            self._between_game_tick()
        else:
            self._lobby_tick()

        self._inputs_processed()

    def _inputs_processed(self):
        for input in self._inputs.values():
            input.processed = True

    def _lobby_tick(self):
        change: bool = False
        for key, value in self._inputs.items():
            if value.space and not value.processed:
                old_state = self._gameState.player_list[key].player.player_status
                self._gameState.player_list[key].player.player_status = \
                    PlayerStatus.READY if old_state == PlayerStatus.NOT_READY else PlayerStatus.NOT_READY
                change = True

        if change:
            self._broadcast_state()

    def _in_game_tick(self):
        for k in player_ticks_to_next_hole.keys():
            player_ticks_to_next_hole[k] -= 1
        for k in player_hole_ticks_left.keys():
            player_hole_ticks_left[k] -= 1
        self.move()

    def _between_game_tick(self):
        pass