import socket
import pickle
import time
import asyncore
import logging
import collections
import threading
from datetime import datetime

from GameObjects.GameState import GameState
from GameObjects.Input.PlayerInput import PlayerInput
from GameObjects.Input.PlayerLobbyInput import PlayerLobbyInput

MAX_MESSAGE_LENGTH = 1024


class Client(threading.Thread, asyncore.dispatcher):

    def __init__(self, host, port, name):
        threading.Thread.__init__(self)
        self._thread = None
        self.log = logging.getLogger('Client (%7s)' % name)
        self._thread_sockets = dict()
        asyncore.dispatcher.__init__(self, map=self._thread_sockets)
        self.daemon = True

        self.host = host
        self.port = port

        self.name = name
        self.log.info('Connecting to host at %s', host)
        self.outbox = collections.deque()
        self._receive_message_event = None
        self.start()

    @property
    def receive_message_event(self):
        return self._receive_message_event

    @receive_message_event.setter
    def receive_message_event(self, value):
        if callable(value):
            self._receive_message_event = value

    def run(self):
        """
                For use when an asyncore.loop is not already running.
                Starts a threaded loop.
                """
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((self.host, self.port))
        asyncore.loop(map=self._thread_sockets)

    def say(self, message):
        self.log.info("Send: {0}".format(type(message)))
        self.outbox.append(pickle.dumps(message))

    def handle_write(self):
        if not self.outbox:
            return
        message = self.outbox.popleft()
        if len(message) > MAX_MESSAGE_LENGTH:
            self.log.error('Message too long')
            return
        self.send(message)

    def handle_read(self):
        message = self.recv(MAX_MESSAGE_LENGTH)
        self.log.info('Received message: %s', message)
        if len(message) > 0:
            message_decode = pickle.loads(message)
            if isinstance(message_decode, GameState) and self._receive_message_event is not None:
                self._receive_message_event(message_decode)


def main():
    logging.basicConfig(level=logging.INFO)
    client = Client("127.0.0.1", 4321, 'test_1')
    client.start()

    lobby = PlayerLobbyInput()
    lobby.create_new_lobby = True
    client.say(lobby)
    input = PlayerInput()
    input.left = True
    client.say(input)
    while (1):
        time.sleep(3)



if __name__ == '__main__':
    main()
