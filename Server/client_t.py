import socket
import pickle
from datetime import datetime

BUFFERSIZE = 512


class Client:
    def __init__(self, address, port):
        self._address = address
        self._port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self._address, self._port))

    def send(self, message):
        print('send data to {0}:{1}'.format(self._address, self._port))
        self.socket.send(message)

    def receive(self):
        recieved = self.socket.recv(BUFFERSIZE)
        print('received data from {0}:{1}'.format(self._address, self._port))
        if recieved:
            return recieved
        else:
            print("no data recieved on {0}:{1}".format(self._address, self._port))


def main():
    client = Client("127.0.0.1", 4321)
    data = client.receive()
    print(pickle.loads(data))
    client.send(pickle.dumps(datetime.now()))


if __name__ == '__main__':
    main()
