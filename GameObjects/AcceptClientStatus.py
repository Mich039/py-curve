

class AcceptClientStatus():

    def __init__(self, ip, port, id):
        self._ip = ip
        self._port = port
        self._id = id

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    @property
    def ip(self):
        return self._ip

    @ip.setter
    def ip(self, value):
        self._ip = value

    @property
    def port(self):
        return self._port

    @port.setter
    def port(self, value):
        self._port = value
