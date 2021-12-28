import pygame
import time
import math
import random

from pygame.constants import HIDDEN
from utils import scale_image, blit_rotate_center

GRASS = scale_image(pygame.image.load("images/grass.jpg"), 1.6)
TRACK = scale_image(pygame.image.load("images/track.png"), 1.6)

#TRACK_BORDER = scale_image(pygame.image.load("imgs/track-border.png"), 0.9)

RED_CAR = scale_image(pygame.image.load("images/main_agent2.png"), 0.55)
GREEN_CAR = scale_image(pygame.image.load("images/police.png"), 0.55)

# WIDTH, HEIGHT = TRACK.get_width(), TRACK.get_height()
WIDTH, HEIGHT = GRASS.get_width(), GRASS.get_height()
print(WIDTH,HEIGHT)
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Racing Game!")

FPS = 60

# setting the path limits
left_x_limit=260
right_x_limit=WIDTH-288

# class to make arbitary vehicles
class Block:
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.speedy = 5
        self.dodged = 0
        
    def update(self):
        self.y = self.y + self.speedy
       # check boundary (block)
        if self.y > WIDTH:
           self.y = 0 - 10
           self.x = random.randrange(left_x_limit,right_x_limit)
           #print(self.x,left_x_limit,right_x_limit-self.width)
           self.dodged = self.dodged + 1

    def draw(self,wn):
        # pygame.draw.rect(wn, (255,0,0), [self.x, self.y, self.width, self.height])
        wn.blit(GREEN_CAR,(self.x,self.y))

class AbstractCar:
    def __init__(self, max_vel, rotation_vel):
        self.img = self.IMG
        self.max_vel = max_vel
        self.vel = 0
        self.x, self.y = self.START_POS
        self.acceleration = 0.1

    def draw(self,win):
        win.blit(self.img,(self.x,self.y))

    def move_forward(self):
        self.vel = min(self.vel + self.acceleration, self.max_vel)

    def movement(self,left=False,right=False):
        if left:
            horizontal = self.vel
            self.x -= horizontal
        elif right:
            horizontal = self.vel
            self.x += horizontal

    def reduce_speed(self):
        self.vel = max(self.vel - self.acceleration / 2, 0)


class PlayerCar(AbstractCar):
    IMG = RED_CAR
    START_POS = (5*HEIGHT/6, WIDTH-450)


def draw(win, images, player_car):
    for img, pos in images:
        win.blit(img, pos)

    player_car.draw(win)
    pygame.display.update()


run = True
clock = pygame.time.Clock()
images = [(GRASS, (0, 0)), (TRACK, (0,0))]
player_car = PlayerCar(4, 4)


block_x = random.randrange(left_x_limit, right_x_limit)
block_y = -100

block = Block(block_x,block_y)

while run:
    clock.tick(FPS)
    block.update()
    draw(WIN, images, player_car)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            break

    block.draw(WIN)
    keys = pygame.key.get_pressed()
    moved = False

    if keys[pygame.K_a] or keys[pygame.K_LEFT]:
        player_car.movement(left=True)
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        player_car.movement(right=True)
    if keys[pygame.K_w] or keys[pygame.K_UP]:
        moved = True
        player_car.move_forward()

    if not moved:
        player_car.reduce_speed()

    pygame.display.update()


pygame.quit()