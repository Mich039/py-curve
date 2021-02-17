import logging
import threading
import time
import random

from GameObjects.GameState import GameState
from GameObjects.Input.PlayerInput import PlayerInput
from GameObjects.Input.PlayerLobbyInput import PlayerLobbyInput
from GameServer.GameServer import GameServer
from Socket.client import Client
from Socket.server import Host

_actions = ["left", "right", "space"]

def broadcast(id: int, state: GameState):
    print("Server id: {id}".format(id=id))
    print(state.player_list[1].head)


def main_test():
    gameServer = GameServer(1)
    gameServer.broadcast = broadcast
    thread = threading.Thread(target=gameServer.start)
    thread.daemon = True
    thread.start()

    time.sleep(1)
    gameServer.add_player(1)
    time.sleep(1)
    pin = PlayerInput()
    pin.space = True
    gameServer.receive_player_input(1, pin)

    time.sleep(1000)

def generate_random_input():
    player_input = PlayerInput()
    random_action = random.sample(_actions, k=1)
    if random_action == "left":
        player_input.left = True
    elif random_action == "right":
        player_input.right = True
    else:
        player_input.space = True
    return player_input

def main_socket_test():
    logging.basicConfig(level=logging.INFO)
    logging.info('Create host')
    host = Host('127.0.0.1', 4321)
    host.start(False)

    client_1 = Client("127.0.0.1", 4321, 'client_1')
    # client_1.start()

    client_2 = Client("127.0.0.1", 4321, 'client_2')
    # client_2.start()

    # create lobby
    lobby_input = PlayerLobbyInput()
    lobby_input.create_new_lobby = True

    client_1.say(lobby_input)

    time.sleep(1)
    # join lobby
    lobby_input_join = PlayerLobbyInput()
    lobby_input_join.lobby_id = 1

    client_2.say(lobby_input_join)

    client_to_send = 1
    while True:
        input = generate_random_input()
        if client_to_send == 1:
            client_1.say(input)
            client_to_send = 2
        elif client_to_send == 2:
            client_2.say(input)
            client_to_send = 3
        elif client_to_send == 3:
            client_1.say(input)
            client_2.say(input)
            client_to_send = 1
        time.sleep(2)

    time.sleep(5)

if __name__ == '__main__':
    # main_test()
    main_socket_test()