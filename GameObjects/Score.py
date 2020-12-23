class Score:

    def __init__(self):
        self._score_points = None
        self._power_up_points = None
        self._deaths = None

    @property
    def score_points(self):
        return self._score_points

    @score_points.setter
    def score_points(self, value):
        self._score_points = value

    @property
    def power_up_points(self):
        return self._score_points

    @power_up_points.setter
    def power_up_points(self, value):
        self._power_up_points = value

    @property
    def deaths(self):
        return self._deaths

    @deaths.setter
    def deaths(self, value):
        self._deaths = value