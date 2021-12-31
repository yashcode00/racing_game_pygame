import pygame
import time
import math
import random

from pygame.constants import HIDDEN
from utils import scale_image, blit_rotate_center

GRASS = scale_image(pygame.image.load("images/grass.jpg"), 1.6)
TRACK = scale_image(pygame.image.load("images/track.png"), 1.6)
TRACK_BORDER = scale_image(pygame.image.load("images/track_border.png"), 1.6)
TRACK_BORDER_MASK = pygame.mask.from_surface(TRACK_BORDER)

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
right_x_limit=WIDTH-300

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
        self.rotation_vel = rotation_vel
        self.angle = 0
        self.x, self.y = self.START_POS
        self.acceleration = 0.1

    def rotate(self, left=False, right=False):
        if left:
            self.angle += self.rotation_vel
        elif right:
            self.angle -= self.rotation_vel

    def draw(self, win):
        blit_rotate_center(win, self.img, (self.x, self.y), self.angle)

    def move_forward(self):
        self.vel = min(self.vel + self.acceleration, self.max_vel)
        self.move()

    def move_backword(self):
        self.vel = min(self.vel - self.acceleration, -self.max_vel/2)
        self.move()

    def move(self):
        radians = math.radians(self.angle)
        vertical = math.cos(radians) * self.vel
        horizontal = math.sin(radians) * self.vel

        self.y -= vertical
        self.x -= horizontal

    def collide(self,mask,x=0,y=0):
        car_mask = pygame.mask.from_surface(self.img)
        offset = (int(self.x -x),int(self.y - y ))
        poi = mask.overlap(car_mask,offset) # returns point of intersetion bw masks
        return poi


class PlayerCar(AbstractCar):
    IMG = RED_CAR
    START_POS = (5*HEIGHT/6, WIDTH-450)

    def reduce_speed(self):
        self.vel = max(self.vel - self.acceleration / 2, 0)
        self.move()

    def bounce(self):
        self.vel = -self.vel
        self.move()



def draw(win, images, player_car):
    for img, pos in images:
        win.blit(img, pos)

    player_car.draw(win)
    pygame.display.update()


def move_player(player_car):
    keys = pygame.key.get_pressed()
    moved = False

    if keys[pygame.K_a]:
        player_car.rotate(left=True)
    if keys[pygame.K_d]:
        player_car.rotate(right=True)
    if keys[pygame.K_w]:
        moved = True
        player_car.move_forward()
    if keys[pygame.K_s]:
        moved = True
        player_car.move_backword()

    if not moved:
        player_car.reduce_speed()

run = True
clock = pygame.time.Clock()
images = [(GRASS, (0, 0)), (TRACK, (0,0)), (TRACK_BORDER, (0,0))]
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
    
    move_player(player_car)

    if player_car.collide(TRACK_BORDER_MASK) != None:
        player_car.bounce()

    pygame.display.update()


pygame.quit()