class Color:

    def __init__(self, red=0, green=0, blue=0):
        self._red = red
        self._green = green
        self._blue = blue

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

    def __hash__(self) -> int:
        return hash((self._red, self._green, self._blue))

    def __eq__(self, o) -> bool:
        return self._red == o._red and self._green == o._green and self._blue == o._blue


