import socket
import asyncore
import pickle
import collections
import logging
import threading
import hashlib
import time

from GameObjects.GameState import GameState
from GameObjects.GameState import LobbyState
from GameObjects.Input.PlayerInput import PlayerInput
from GameObjects.Input.PlayerLobbyInput import PlayerLobbyInput
from GameServer.GameServer import GameServer

MAX_MESSAGE_LENGTH = 1024  # message length

_game_servers = dict()  # {key: GameServer; value: List<RemoteClient>()}
_game_server_ids = 1
_lock = threading.Lock()

_sentinel = b'\x00\x00END_MESSAGE!\x00\x00'[:MAX_MESSAGE_LENGTH]

def create_game_server():
    """
    Creates a new GameServer and set a id for it.
    :return:
    """
    with _lock:
        global _game_server_ids
        id = _game_server_ids
        _game_server_ids += 1
        return GameServer(id)


class RemoteClient(asyncore.dispatcher):
    """Wraps a remote client socket."""

    def __init__(self, host, socket, address, server_broadcast, remove_game_server):
        asyncore.dispatcher.__init__(self, socket)
        self._log = logging.getLogger('RemoteClient {0}'.format(address))
        to_hash = address[0] + str(address[1])
        self._client_id = hashlib.sha256(to_hash.encode()).hexdigest()
        self._log.info(f'Client-Id {self._client_id}')
        self._host = host
        self._outbox = collections.deque()
        self._game_server = None
        self._server_broadcast = server_broadcast
        self._remove_game_server = remove_game_server

    def handle_read(self):
        """
        Handle the reading from the socket stream.
        Check the type of the received object and choose further actions.
        :return:
        """
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
        """
        Creates, join or leave a lobby.
        On create, a new GameServer is created and the player joins it.
        On join, the player joins an existing GameServer by Id.
        On remove, removes the player from an existing GameServer.
        :param client_message:
        :return:
        """
        global _game_servers
        if client_message.create_new_lobby:  # create new lobby
            self._log.info('creating lobby ...')
            game_server = create_game_server()
            # GameServer has to be started
            thread = threading.Thread(target=game_server.start)
            thread.start()
            # game_server.start()
            self._log.info('GameServer created with id {0}'.format(game_server.id))
            game_server.broadcast = self._server_broadcast
            game_server.remove_game_server = self._remove_game_server
            _game_servers[game_server] = [self]
            self._game_server = game_server
            self._game_server.add_player(self._client_id, client_message.username)
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
            _game_servers[game_server].append(self)  # changed by Sebastian: list needs append
            self._game_server.add_player(self._client_id, client_message.username)
            self._log.info('Add Player to Lobby')
        elif client_message.leave_lobby:  # leave lobby
            self._log.info('leaving lobby ...')
            if self._game_server is not None:
                self._game_server.remove_player(self._client_id)
        else:
            self._log.error('Received invalid PlayerLobbyInput')

    def handle_player_input(self, client_message: PlayerInput):
        """
        Redirect the player input to the GameServer
        :param client_message:
        :return:
        """
        if self._game_server is None:
            self._log.error('Game Server is empty')
            return  # TODO: maybe exception
        self._game_server.receive_player_input(self._client_id, client_message)

    def say(self, message):
        """
        Say a object to the socket client.
        The object will be converted to a byte array.
        :param message: A simple object
        :return:
        """
        self._outbox.append(pickle.dumps(message))

    def handle_write(self):
        """
        Handles the sending of messages to the socket client.
        This method will be periodically called.
        :return:
        """
        if not self._outbox:
            return
        message = self._outbox.popleft()
        self.send(message)
        time.sleep(0.001)
        self.send(_sentinel)

    def handle_close(self) -> None:
        """
        Handles the closing of the RemoteClient (socket connection).
        Removes player if the socket is closed.
        :return:
        """
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

    def start(self, blocking=False):
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
        """
        Handles the accepting of a new socket client.
        Creates a RemoteClient for each new socket client.
        :return:
        """
        s, addr = self.accept()  # For the remote client.
        self.log.info('Accepted client at %s', addr)
        self.remote_clients.append(RemoteClient(self, s, addr, self.broadcast_game_server, self.remove_game_server))

    def broadcast(self, message):
        """
        Broadcast a message to all RemoteClients
        :param message:
        :return:
        """
        self.log.info('Broadcasting message %s', message)
        for remote_client in self.remote_clients:
            remote_client.say(message)

    def broadcast_game_server(self, game_server_id: int, message):
        """
        Broadcast a message to all RemoteClients from a GameServer.
        :param game_server_id:
        :param message:
        :return:
        """
        self.log.info('Broadcasting message from game_server %s', message)
        keys = list(_game_servers.keys())
        game_server = next((x for x in keys if x.id == game_server_id), None)
        if game_server is not None:
            for remote_client in _game_servers[game_server]:
                remote_client.say(message)

    def remove_game_server(self, game_server: GameServer):
        """
        Remove a GameServer.
        :param game_server: The game server to be deleted
        """
        try:
            _game_servers.pop(game_server)
            self.log.info(f" Game server with id {game_server.id} closed.")
        except:
            pass  # ignore


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logging.info('Create host')
    host = Host('127.0.0.1', 4321)
    # host.start()
    asyncore.loop()
