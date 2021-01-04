class Color:

    def __init__(self):
        self._red = 0
        self._green = 0
        self._blue = 0

    @property
    def red(self) -> int:
        return self._red

    @red.setter
    def red(self, value: int):
        self._red = value

    @property
    def green(self) -> int:
        return self._green

    @green.setter
    def green(self, value: int):
        self._green = value

    @property
    def blue(self) -> int:
        return self._blue

    @blue.setter
    def blue(self, value: int):
        self._blue = value
