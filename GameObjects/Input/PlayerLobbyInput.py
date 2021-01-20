class PlayerLobbyInput:

    def __init__(self):
        self._lobby_id = 0
        self._create_new_lobby = False
        self._username = ''
        self._leave_lobby = False

    @property
    def leave_lobby(self):
        return self._leave_lobby

    @leave_lobby.setter
    def leave_lobby(self, value):
        self._leave_lobby = value

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, value):
        self._username = value

    @property
    def lobby_id(self) -> int:
        return self._lobby_id

    @lobby_id.setter
    def lobby_id(self, value: int):
        self._lobby_id = value

    @property
    def create_new_lobby(self) -> bool:
        return self._create_new_lobby

    @create_new_lobby.setter
    def create_new_lobby(self, value: bool):
        self._create_new_lobby = value
