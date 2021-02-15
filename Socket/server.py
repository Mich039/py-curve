import socket
import asyncore
import pickle
import collections
import logging
import threading
import hashlib

from GameObjects.GameState import GameState
from GameObjects.GameState import LobbyState
from GameObjects.Input.PlayerInput import PlayerInput
from GameObjects.Input.PlayerLobbyInput import PlayerLobbyInput
from GameServer.DummyGameServer import GameServer

BUFFERSIZE = 512

MAX_MESSAGE_LENGTH = 1024  # message length

_game_servers = dict() # {key: GameServer; value: List<RemoteClient>()}
_game_server_ids = 1
_lock = threading.Lock()

def create_game_server():
    with _lock:
        global _game_server_ids
        id = _game_server_ids
        _game_server_ids += 1
        return GameServer(id)

class RemoteClient(asyncore.dispatcher):
    """Wraps a remote client socket."""

    def __init__(self, host, socket, address, server_broadcast):
        asyncore.dispatcher.__init__(self, socket)
        self._log = logging.getLogger('RemoteClient {0}'.format(address))
        #self._client_id = hashlib.sha256(to_hash).hexdigest() #TODO
        #self._log.info(f'Client-Id {self._client_id}')
        self._host = host
        self._outbox = collections.deque()
        self._game_server = None
        self._server_broadcast = server_broadcast

    def say(self, message):
        self._outbox.append(message)

    def handle_read(self):
        self._log.info('Read')
        received_message = self.recv(MAX_MESSAGE_LENGTH)
        if(len(received_message) > 0):
            client_message = pickle.loads(received_message)
        else:
            self._log.info('received message is empty')
            return

        if isinstance(client_message, PlayerLobbyInput):
            self._log.info('received PlayerLobbyInput')
            self.handle_lobby_input(client_message)
        elif isinstance(client_message, PlayerInput):
            self._log.info('received PlayerInput')
            self.handle_player_input(client_message)
        else:
            self._log.info('received invalid input from client: Type {0}'.format(type(client_message)))

    def handle_lobby_input(self, client_message: PlayerLobbyInput):
        global _game_servers
        if client_message.create_new_lobby: #create new lobby
            game_server = create_game_server()
            game_server.broadcast = self._server_broadcast
            _game_servers[game_server] = [self]
            self._game_server = game_server
            game_state = GameState()
            game_state.state = LobbyState.LOBBY
            self._log.info('Lobby created')
        elif client_message.lobby_id > 0 and not client_message.create_new_lobby:
            keys = list(_game_servers.keys())
            game_server = next((x for x in keys if x.id == client_message.lobby_id), None)
            if game_server == None:
                return # TODO: maybe send an error back
            self._game_server = game_server
            _game_servers[game_server].push(self)
            self._log.info('Add Player to Lobby')
        elif client_message._leave_lobby:
            self._log.info('Leave Lobby')
            pass #TODO remove player from GameServer
        else:
            self._log.error('Received invalid PlayerLobbyInput')

    def handle_player_input(self, client_message: PlayerInput):
        if self._game_server == None:
            self._log.error('Game Server is empty')
            return # TODO: maybe exception
        #self._game_server.input(self, client_message)

    def handle_write(self):
        if not self._outbox:
            return
        message = self._outbox.popleft()
        if len(message) > MAX_MESSAGE_LENGTH:
            raise ValueError('Message too long')
        self.send(pickle.dumps(message))

    def handle_close(self) -> None:
        super(RemoteClient, self).handle_close()
        pass


class Host(asyncore.dispatcher):
    log = logging.getLogger('Host')

    def __init__(self, address, port):
        asyncore.dispatcher.__init__(self)

        self._thread = None

        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((address, port))
        self.listen(1)
        self.remote_clients = []

    def start(self):
        """
                For use when an asyncore.loop is not already running.
                Starts a threaded loop.
                """
        if self._thread is not None:
            return

        self._thread = threading.Thread(target=asyncore.loop, kwargs={'timeout': 1})
        self._thread.daemon = True
        self._thread.start()

    def handle_accept(self):
        s, addr = self.accept()  # For the remote client.
        self.log.info('Accepted client at %s', addr)
        self.remote_clients.append(RemoteClient(self, s, addr, self.broadcast))
        #TODO: send lobbies to client

    def handle_read(self):
        self.log.info('Received message: %s', self.read(MAX_MESSAGE_LENGTH))

    def broadcast(self, message):
        self.log.info('Broadcasting message: %s', message)
        for remote_client in self.remote_clients:
            remote_client.say(message)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logging.info('Create host')
    host = Host('localhost', 4321)
    # host.start()
    asyncore.loop()
