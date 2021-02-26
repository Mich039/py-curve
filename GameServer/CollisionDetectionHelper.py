from GameObjects.Point import Point
from GameServer import ServerConstants


def is_relevant(p1: Point, p2: Point):
    """
    Checks if two given Points are within a given range.
    Range is defined in ServerConstants.
    (Absolute Difference in X- or Y-Axis)
    """
    return p2.x + ServerConstants.CHECK_DISTANCE < p1.x or p2.x - ServerConstants.CHECK_DISTANCE > p1.x \
           and p2.y + ServerConstants.CHECK_DISTANCE < p1.y or p2.y - ServerConstants.CHECK_DISTANCE > p1.y


def on_segment(f, b, t):
    """
    Takes 3 collinear points and checks whether point m is between
    f and t
    :param f: f(rom) point
    :param b: point that might be b(etween)
    :param t: t(o) point
    :return:
    """
    if ((b.x <= max(f.x, t.x)) and (b.x >= min(f.x, t.x)) and
            (b.y <= max(f.y, t.y)) and (b.y >= min(f.y, t.y))):
        return True
    return False


def orientation(p: Point, q, r):
    # See https://www.geeksforgeeks.org/orientation-3-ordered-points/amp/

    val = (float(q.y - p.y) * (r.x - q.x)) - (float(q.x - p.x) * (r.y - q.y))
    if val > 0:
        # Clockwise orientation
        return 1
    elif val < 0:
        # Counterclockwise orientation
        return 2
    else:
        # Collinear orientation
        return 0


def check_collision(p1, q1, p2, q2):
    o1 = orientation(p1, q1, p2)
    o2 = orientation(p1, q1, q2)
    o3 = orientation(p2, q2, p1)
    o4 = orientation(p2, q2, q1)

    # General case
    if (o1 != o2) and (o3 != o4):
        return True

    # Special Cases

    # p1 , q1 and p2 are collinear and p2 lies on segment p1q1
    if (o1 == 0) and on_segment(p1, p2, q1):
        return True

    # p1 , q1 and q2 are collinear and q2 lies on segment p1q1
    if (o2 == 0) and on_segment(p1, q2, q1):
        return True

    # p2 , q2 and p1 are collinear and p1 lies on segment p2q2
    if (o3 == 0) and on_segment(p2, p1, q2):
        return True

    # p2 , q2 and q1 are collinear and q1 lies on segment p2q2
    if (o4 == 0) and on_segment(p2, q1, q2):
        return True

    # If none of the cases
    return False