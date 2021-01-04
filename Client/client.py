import pygame
import math
from datetime import datetime, timedelta
import random

width = 1000
height = 1000
base_speed = 5.0
win = pygame.display.set_mode((width, height))
pygame.display.set_caption("Client")

clientNumber = 0

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
            #for p in self.points:
            #    pygame.draw.circle(win, self.color, p, 3, 0)
            pygame.draw.lines(win, self.color, points=pts, closed=False, width=4)
        if len(self.curr_line) > 2:
            pygame.draw.lines(win, self.color, points=self.curr_line, closed=False, width=4)


    def move(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            self.rotate_by(-3)

        if keys[pygame.K_RIGHT]:
            self.rotate_by(3)

        #if keys[pygame.K_UP]:
        #    self.y -= self.vel

        #if keys[pygame.K_DOWN]:
        #    self.y += self.vel
        self.posX += base_speed * self.x
        self.posY += base_speed * self.y

        self.curr_line.append(self.point)
        self.point = (self.posX, self.posY)
        if random.random() < 0.005:
            self.invisible_since = datetime.now()
            self.points.append(self.curr_line)
            self.curr_line = []


def redrawWindow(win, player):
    win.fill((255, 255, 255))
    player.draw(win)
    pygame.display.update()


if __name__ == '__main__':
    run = True
    p = Player(50, 50, 10, 10, (0, 255, 0))
    clock = pygame.time.Clock()
    while run:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()

        p.move()
        redrawWindow(win, p)