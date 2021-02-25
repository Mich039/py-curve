from typing import List, Optional

from GameObjects.Point import Point
from GameServer import ServerConstants


class ListSegment:

    def __init__(self):
        self._min: Point = Point(ServerConstants.PLAY_AREA_SIZE, ServerConstants.PLAY_AREA_SIZE)
        self._max: Point = Point(0, 0)
        self._list: List[Point] = []

    @property
    def min(self) -> Optional[Point]:
        return self._min

    @property
    def max(self) -> Optional[Point]:
        return self._max

    @property
    def list(self) -> List[Point]:
        return self._list

    def add_point(self, point: Point):
        """
        Adds a Point to the ListSegment.
        This also updates the min and max properties of the ListSegment accordingly

        :param point: The Point that will get added to the ListSegment
        """
        if self._min.x >= point.x:
            self._min.x = int(point.x)
        if self._min.y >= point.y:
            self._min.y = int(point.y)
        if self._max.x <= point.x:
            self._max.x = int(point.x)
        if self._max.y <= point.y:
            self._max.y = int(point.y)
        self._list.append(point)

    def point_in_segment(self, point: Point) -> bool:
        """
        Checks if the given Point is within the boundlingbox of the ListSegment

        :param point: The Point to be checked
        :return: If the Point is within the bounding box of the ListSegment true, otherwise False.
        """
        return self._max is not None and self._min is not None and self._min.x <= point.x <= self._max.x and self._min.y <= point.y <= self._max.y
