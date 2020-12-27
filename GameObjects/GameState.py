class GameStats:

    def __init__(self):
        self._player_list = None
        self._ground_power_up = None
        self._state = None

    @property
    def player_list(self):
        return self._player_list

    @player_list.setter
    def player_list(self, value):
        self._player_list = value

    @property
    def ground_power_up(self):
        return self._ground_power_up

    @ground_power_up.setter
    def ground_power_up(self, value):
        self._ground_power_up = value

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = value
