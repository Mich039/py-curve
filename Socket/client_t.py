import socket
import pickle
import time
import asyncore
import logging
import collections
import threading
from datetime import datetime

MAX_MESSAGE_LENGTH = 1024


class Client(asyncore.dispatcher):

    def __init__(self, host, port, name):
        asyncore.dispatcher.__init__(self)

        self._thread = None

        self.log = logging.getLogger('Client (%7s)' % name)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.name = name
        self.log.info('Connecting to host at %s', host)
        self.connect((host, port))
        self.outbox = collections.deque()

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

    def say(self, message):
        self.outbox.append(message)
        self.log.info('Enqueued message: %s', message)

    def handle_write(self):
        if not self.outbox:
            return
        message = self.outbox.popleft()
        if len(message) > MAX_MESSAGE_LENGTH:
            raise ValueError('Message too long')
        self.send(message)

    def handle_read(self):
        message = self.recv(MAX_MESSAGE_LENGTH)
        self.log.info('Received message: %s', message)


def main():
    logging.basicConfig(level=logging.INFO)
    client = Client("127.0.0.1", 4321, 'test_1')
    client.start()
    client.say(pickle.dumps(datetime.now()))

    while (1):
        time.sleep(1)
        client.say(pickle.dumps(datetime.now()))


if __name__ == '__main__':
    main()
