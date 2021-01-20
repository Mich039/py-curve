class GameServer:
    def __init__(self, id: int):
        self._id = id
        self._broadcast = None

    @property
    def id(self):
        return id

    @id.setter
    def id(self, value):
        id = value

    @property
    def broadcast(self):
        return self._broadcast

    @broadcast.setter
    def broadcast(self, value):
        self._broadcast = value

