class Player:

    def __init__(self):
        self._name = None
        self._player_status = None
        self._color = None
        self._head = None
        self._body = None
        self._active_power_ups = None
        self._score = None

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def player_status(self):
        return self._player_status

    @player_status.setter
    def player_status(self, value):
        self._player_status = value

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        self._color = value

    @property
    def head(self):
        return self._head

    @head.setter
    def head(self, value):
        self._head = value

    @property
    def body(self):
        return self._body

    @body.setter
    def body(self, value):
        self._body = value

    @property
    def active_power_ups(self):
        return self._active_power_ups

    @active_power_ups.setter
    def active_power_ups(self, value):
        self._active_power_ups = value

    @property
    def score(self):
        return self._score

    @score.setter
    def score(self, value):
        self._score = value
