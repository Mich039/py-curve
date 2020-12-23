import socket
import asyncore
import select
import random
import pickle
import time

BUFFERSIZE = 512

outgoing = []


class MainServer(asyncore.dispatcher):
    def __init__(self, port):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        print("socket create on port '{0}'".format(port))
        self.bind(('', port))
        self.listen(10)

    def handle_accept(self):
        conn, addr = self.accept()
        print('Connection address:' + addr[0] + " " + str(addr[1]))
        outgoing.append(conn)
        playerid = random.randint(1000, 1000000)
        conn.send(pickle.dumps(['id update', playerid]))
        HandleConnection(conn)


class HandleConnection(asyncore.dispatcher_with_send):
    def handle_read(self):
        recievedData = self.recv(BUFFERSIZE)
        if recievedData:
            print(pickle.loads(recievedData))
        else:
            self.close()


def main():
    MainServer(4321)
    asyncore.loop()


if __name__ == '__main__':
    main()
