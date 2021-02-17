class Point:

    def __init__(self, x=0, y=0):
        self._x = x
        self._y = y

    @property
    def x(self) -> int:
        return self._x

    @x.setter
    def x(self, value: int):
        self._x = value

    @property
    def y(self) -> int:
        return self._y

    @y.setter
    def y(self, value: int):
        self._y = value

    def __str__(self) -> str:
        return "Point(x:{x}, y:{y})".format(x=self.x, y=self.y)

