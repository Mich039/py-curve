import pygame
import math
from datetime import datetime, timedelta
import random

width = 1000
height = 1000
base_speed = 1.0
win = pygame.display.set_mode((width, height))
pygame.display.set_caption("Client")

clientNumber = 0

def withinRadius(center, pt, radius):
    if pt.x + radius < center.x or pt.x - radius > center.x:
        return False
    if pt.y + radius < center.y or pt.y - radius > center.y:
        return False
    return True


def PointsToTuple(points):
    res = []
    for p in points:
        res.append((p.x, p.y))
    return res

def onSegment(p, q, r):
    if ( (q.x <= max(p.x, r.x)) and (q.x >= min(p.x, r.x)) and
           (q.y <= max(p.y, r.y)) and (q.y >= min(p.y, r.y))):
        return True
    return False


def orientation(p, q, r):
    # to find the orientation of an ordered triplet (p,q,r)
    # function returns the following values:
    # 0 : Colinear points
    # 1 : Clockwise points
    # 2 : Counterclockwise

    # See https://www.geeksforgeeks.org/orientation-3-ordered-points/amp/
    # for details of below formula.

    val = (float(q.y - p.y) * (r.x - q.x)) - (float(q.x - p.x) * (r.y - q.y))
    if (val > 0):

        # Clockwise orientation
        return 1
    elif (val < 0):

        # Counterclockwise orientation
        return 2
    else:

        # Colinear orientation
        return 0

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Player:
    def __init__(self, posx, posy, width, height, color):
        self.degrees = math.pi/2
        self.x = 1
        self.y = 0
        self.posX = posx
        self.posY = posy
        self.width = width
        self.height = height
        self.color = color
        self.point = (self.posX, self.posY)
        self.vel = 3
        self.curr_line = []
        self.points = []
        self.invisible_since = None

    def checkCollision(self, p1,q1,p2,q2):
        #print(f"from1: {p1.x}, {p1.y} - to1: {q1.x}, {q1.y}")
        #print(f"from2: {p2.x}, {p2.y} - to2: {q2.x}, {q2.y}")
        o1 = orientation(p1, q1, p2)
        o2 = orientation(p1, q1, q2)
        o3 = orientation(p2, q2, p1)
        o4 = orientation(p2, q2, q1)

        # General case
        if ((o1 != o2) and (o3 != o4)):
            return True

        # Special Cases

        # p1 , q1 and p2 are colinear and p2 lies on segment p1q1
        if ((o1 == 0) and onSegment(p1, p2, q1)):
            return True

        # p1 , q1 and q2 are colinear and q2 lies on segment p1q1
        if ((o2 == 0) and onSegment(p1, q2, q1)):
            return True

        # p2 , q2 and p1 are colinear and p1 lies on segment p2q2
        if ((o3 == 0) and onSegment(p2, p1, q2)):
            return True

        # p2 , q2 and q1 are colinear and q1 lies on segment p2q2
        if ((o4 == 0) and onSegment(p2, q1, q2)):
            return True

        # If none of the cases
        return False

    def rotate_by(self, deg):
        self.degrees += math.radians(deg)
        #print(f"xVorher: {self.x}")
        self.x = math.sin(self.degrees)
        #print(f"xAfter: {self.x}")
        self.y = -math.cos(self.degrees)

    def draw(self, win):
        #print(self.points)
        for pts in self.points:
            if len(pts) < 2:
                continue
            pts = PointsToTuple(pts)
            #for p in self.points:
            #    pygame.draw.circle(win, self.color, p, 3, 0)
            pygame.draw.lines(win, self.color, points=pts, closed=False, width=4)
        if len(self.curr_line) > 2:
            toDraw = PointsToTuple(self.curr_line)
            pygame.draw.lines(win, self.color, points=toDraw, closed=False, width=4)


    def move(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            self.rotate_by(-2)

        if keys[pygame.K_RIGHT]:
            self.rotate_by(2)

        #if keys[pygame.K_UP]:
        #    self.y -= self.vel

        #if keys[pygame.K_DOWN]:
        #    self.y += self.vel
        self.posX += base_speed * self.x
        self.posY += base_speed * self.y

        self.point = Point(self.posX, self.posY)

        if self.invisible_since:
            if datetime.now() - self.invisible_since > timedelta(microseconds=random.randint(50000, 100000)):
                self.invisible_since = None
        else:
            for sl in self.points:
                count = 0
                length = len(sl)
                startingPoint = None
                lastPoint = None
                for p in sl:
                    count = count + 1
                    if not withinRadius(self.point, p, 5):
                        continue
                    if count % 2 == 0:
                        continue
                    if p == startingPoint:
                        break
                    if startingPoint is None:
                        startingPoint = p
                        lastPoint = p
                    else:
                        if len(self.curr_line) > 0:
                            if(self.checkCollision(self.point, self.curr_line[len(self.curr_line) - 1], lastPoint, p)):
                                print(f"HIT: {count}")
                        lastPoint = p
            self.curr_line.append(self.point)
            if random.random() < 0.005:
                self.invisible_since = datetime.now()
                self.points.append(self.curr_line)
                self.curr_line = []


background_image = pygame.image.load("BG.jpeg").convert()

def redrawWindow(win, player):
    #win.fill((50, 50, 50))
    win.blit(background_image, [0, 0])
    player.draw(win)
    pygame.display.update()


if __name__ == '__main__':
    run = True
    p = Player(50, 50, 10, 10, (0, 255, 0))
    clock = pygame.time.Clock()
    while run:
        clock.tick(100)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()

        p.move()
        redrawWindow(win, p)
