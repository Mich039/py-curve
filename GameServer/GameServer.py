import math
from datetime import datetime, timedelta
from typing import Dict

import pygame
import random
import sched, time
import GameObjects
from GameObjects.GameState import GameState
from GameObjects.Player import Player
from GameObjects.Input.PlayerInput import PlayerInput

TICK_RATE = 1.0
BASE_SPEED = 1.0
player_states: Dict[Player, PlayerInput] = dict()
player_ticks_to_next_hole: Dict[Player, int] = dict()
player_hole_ticks_left: Dict[Player, int] = dict()


class GameServer:
    # Add, input, remove
    def __init__(self, id: int):
        self._id = id
        self._gameState = GameState()
        self._broadcast = None
        self._inputs: Dict[int, PlayerInput] = dict()
        self._scheduler: sched.scheduler = sched.scheduler(time.time, time.sleep)
        self._canceled: bool

    def start(self):
        self._scheduler.enter(delay=0, priority=0, action=self.tick, argument=(self,))

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
        self._gameState.player_list.append(Player(id))

    def receive_player_input(self, id: int, player_input: PlayerInput):
        self._inputs[id] = player_input

    def remove_player(self, id: int):
        self._gameState.leave(id)

    def is_visible(self, player: Player):
        if player_hole_ticks_left.get(player, 0) > 0:
            return False
        return True

    def create_hole_for(self, player: Player):
        player.body.append([])
        if is_visible(player):
            tick_length = random.random(50, 200)
            player_hole_ticks_left[player] = tick_length

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
                player.points.append(player.curr_line)
                player.curr_line = []

    def tick(self):
        if not self._canceled:
            self._scheduler.enterabs(time=time.time() + 1 / TICK_RATE, priority=0, action=self.tick, argument=(self,))

        for k in player_ticks_to_next_hole.keys():
            player_ticks_to_next_hole[k] -= 1
        for k in player_hole_ticks_left.keys():
            player_hole_ticks_left[k] -= 1
        self.move()
