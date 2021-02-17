class Score:

    def __init__(self):
        self._score_points = 0
        self._power_up_points = 0
        self._deaths = 0

    @property
    def score_points(self) -> int:
        return self._score_points

    @score_points.setter
    def score_points(self, value: int):
        self._score_points = value

    @property
    def power_up_points(self) -> int:
        return self._score_points

    @power_up_points.setter
    def power_up_points(self, value: int):
        self._power_up_points = value

    @property
    def deaths(self) -> int:
        return self._deaths

    @deaths.setter
    def deaths(self, value: int):
        self._deaths = value
