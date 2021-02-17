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
from GameServer.GameServer import GameServer

BUFFERSIZE = 512
MAX_MESSAGE_LENGTH = 1024  # message length

_game_servers = dict()  # {key: GameServer; value: List<RemoteClient>()}
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
        to_hash = address[0] + str(address[1])
        self._client_id = hashlib.sha256(to_hash.encode()).hexdigest()
        self._log.info(f'Client-Id {self._client_id}')
        self._host = host
        self._outbox = collections.deque()
        self._game_server = None
        self._server_broadcast = server_broadcast

    def handle_read(self):
        self._log.info('Read')
        received_message = self.recv(MAX_MESSAGE_LENGTH)
        if len(received_message) > 0:
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
        if client_message.create_new_lobby:  # create new lobby
            self._log.info('creating lobby ...')
            game_server = create_game_server()
            self._log.info('GameServer created with id {0}'.format(game_server.id))
            game_server.broadcast = self._server_broadcast
            _game_servers[game_server] = [self]
            self._game_server = game_server
            game_state = GameState()
            game_state.state = LobbyState.LOBBY
            self._log.info('Lobby created')
        elif client_message.lobby_id > 0 \
                and not client_message.create_new_lobby:  # join lobby
            self._log.info('joining lobby ...')
            keys = list(_game_servers.keys())
            game_server = next((x for x in keys if x.id == client_message.lobby_id), None)
            if game_server is None:
                self._log.error('No GamerServer found for joining. Id: {0}'.format(client_message.lobby_id))
                return  # TODO: maybe send an error back
            self._game_server = game_server
            _game_servers[game_server].append(self)
            self._log.info('Add Player to Lobby')
        elif client_message.leave_lobby:  # leave lobby
            self._log.info('leaving lobby ...')
            if self._game_server is not None:
                self._game_server.remove_player(self._client_id)
        else:
            self._log.error('Received invalid PlayerLobbyInput')

    def handle_player_input(self, client_message: PlayerInput):
        if self._game_server is None:
            self._log.error('Game Server is empty')
            return  # TODO: maybe exception
        self._game_server.receive_player_input(self._client_id, client_message)

    def say(self, message):
        self._outbox.append(pickle.dumps(message))

    def handle_write(self):
        if not self._outbox:
            return
        message = self._outbox.popleft()
        if len(message) > MAX_MESSAGE_LENGTH:
            raise ValueError('Message too long')
        self.send(message)

    def handle_close(self) -> None:
        # super(RemoteClient, self).handle_close()
        self._log.info('leaving lobby ... (handle_close)')
        if self._game_server is not None:
            self._game_server.remove_player(self._client_id)
        self.close()


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

    def start(self, blocking = False):
        """
                For use when an asyncore.loop is not already running.
                Starts a threaded loop.
        """
        if self._thread is not None:
            return

        self._thread = threading.Thread(target=asyncore.loop, kwargs={'timeout': 1})
        self._thread.daemon = True
        self._thread.start()
        if blocking:
            self._thread.join()

    def handle_accept(self):
        s, addr = self.accept()  # For the remote client.
        self.log.info('Accepted client at %s', addr)
        self.remote_clients.append(RemoteClient(self, s, addr, self.broadcast_game_server))
        # TODO: send lobbies to client

    def handle_read(self):
        self.log.info('Received message: %s', self.read(MAX_MESSAGE_LENGTH))

    def broadcast(self, message):
        self.log.info('Broadcasting message %s', message)
        for remote_client in self.remote_clients:
            remote_client.say(message)

    def broadcast_game_server(self, game_server_id: int, message):
        self.log.info('Broadcasting message from game_server %s', message)
        keys = list(_game_servers.keys())
        game_server = next((x for x in keys if x.id == game_server_id), None)
        if game_server is not None:
            for remote_client in _game_servers[game_server]:
                remote_client.say(message)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logging.info('Create host')
    host = Host('192.168.100.11', 4321)
    # host.start()
    asyncore.loop()
