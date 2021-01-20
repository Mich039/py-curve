import math
from datetime import datetime
from typing import Dict

import random
from GameObjects.Player import Player
from GameObjects.Input.PlayerInput import PlayerInput

BASE_SPEED = 1.0
player_states: Dict[Player, PlayerInput] = dict()
player_ticks_to_next_hole: Dict[Player, int] = dict()
player_hole_ticks_left: Dict[Player, int] = dict()


def is_visible(player: Player):
    if player_hole_ticks_left.get(player, 0) > 0:
        return False
    return True

def create_hole_for(player: Player):
    player.body.append([])
    if is_visible(player):
        tick_length = random.random(50, 200)
        player_hole_ticks_left[player] = tick_length

def rotate_by(player: Player, angle: int):
    Player.angle += math.radians(angle)
    # print(f"xVorher: {self.x}")
    #x = math.sin(angle)
    # print(f"xAfter: {self.x}")
    #y = -math.cos(angle)

def move(player: Player, player_input: PlayerInput):
    if player_input.left:
        rotate_by(player, -5)

    if player_input.right:
        rotate_by(player, 5)

    player.head.x += BASE_SPEED * math.sin(player.angle)
    player.head.y += BASE_SPEED * -math.cos(player.angle)

    #self.point = (self.posX, self.posY)

    if is_visible(player):
        if len(player.body) == 0:
            player.body.append([])

        player.body[len(player.body) - 1].append((player.head.x, player.head.y))
        if random.random() < 0.005:
            player.invisible_since = datetime.now()
            player.points.append(player.curr_line)
            player.curr_line = []

def tick():
    for k in player_ticks_to_next_hole.keys():
        player_ticks_to_next_hole[k] -= 1
    for k in player_hole_ticks_left.keys():
        player_hole_ticks_left[k] -= 1
    move()
