import socket
import asyncore
import random
import pickle
import selectors
import collections
import logging


BUFFERSIZE = 512

MAX_MESSAGE_LENGTH = 1024  # message length

outgoing = []

class RemoteClient(asyncore.dispatcher):

    """Wraps a remote client socket."""


    def __init__(self, host, socket, address):
        asyncore.dispatcher.__init__(self, socket)
        self.host = host
        self.outbox = collections.deque()

    def say(self, message):
        self.outbox.append(message)

    def handle_read(self):
        client_message = self.recv(MAX_MESSAGE_LENGTH)
        self.host.broadcast(client_message)

    def handle_write(self):
        if not self.outbox:
            return
        message = self.outbox.popleft()
        if len(message) > MAX_MESSAGE_LENGTH:
            raise ValueError('Message too long')
        self.send(message)

class MainServer(asyncore.dispatcher):

    log = logging.getLogger('Host')

    def __init__(self, port):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.log.info("socket create on port '{0}'".format(port))
        self.bind(('', port))
        self.listen(10)
        self.clients = []

    def handle_accept(self):
        conn, addr = self.accept()
        self.log.info('Connection address:' + addr[0] + " " + str(addr[1]))
        client = RemoteClient(self, conn, addr)
        self.clients.append(client)
        playerid = random.randint(1000, 1000000)
        client.say(pickle.dumps(['id update', playerid]))

    def handle_read(self):
        message = self.recv(MAX_MESSAGE_LENGTH);
        self.log.info('Server received message')

    def broadcast(self, message):
        self.log.info('broadcast message to clients')
        for client in self.clients:
            client.say(message)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logging.info('Create host')
    MainServer(4321)
    asyncore.loop()
