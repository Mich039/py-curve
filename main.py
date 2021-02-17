import threading
import time

from GameObjects.GameState import GameState
from GameObjects.Input.PlayerInput import PlayerInput
from GameServer.GameServer import GameServer


def broadcast(id: int, state: GameState):
    print("Server id: {id}".format(id=id))
    print(state.player_list[1].player_status)


if __name__ == '__main__':
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
