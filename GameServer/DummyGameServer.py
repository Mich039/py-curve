class GameServer:
    def __init__(self, id: int):
        self._id = id

    @property
    def id(self):
        return id

    @id.setter
    def id(self, value):
        id = value