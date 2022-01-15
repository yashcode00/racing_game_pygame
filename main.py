import pygame
import time
import math
import random
import os
import numpy as np

pygame.init()
font1 = pygame.font.Font('freesansbold.ttf', 32)
pygame.mixer.init()

from pygame.constants import HIDDEN
from utils import scale_image, blit_rotate_center

all_vehicles=os.listdir('images')
for val in ['crash.png', 'grass.jpg', 'main_agent.png', 'main_agent2.png','track.png','Thumbs.db','speedometer.png']:
    all_vehicles.remove(val)
# print(all_vehicles)

GRASS = scale_image(pygame.image.load("images/grass.jpg"), 1.6)
TRACK = scale_image(pygame.image.load("images/track.png"), 1.6)
CRASH = scale_image(pygame.image.load("images/crash.png"),0.5)
SPEEDOMETER=scale_image(pygame.image.load("images/speedometer.png"), 0.45)
INITIAL_VELOCITY = 20
sound_accelerate=pygame.mixer.Sound("sounds/car_acceleration.mp3")
sound_accelerate.set_volume(0)

#TRACK_BORDER = scale_image(pygame.image.load("imgs/track-border.png"), 0.9)

RED_CAR = scale_image(pygame.image.load("images/main_agent2.png"), 0.55)
GREEN_CAR = scale_image(pygame.image.load("images/police.png"), 0.55)

# WIDTH, HEIGHT = TRACK.get_width(), TRACK.get_height()
WIDTH, HEIGHT = GRASS.get_width(), GRASS.get_height()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Racing Game!")

FPS = 60

# setting the path limits
left_x_limit=260
right_x_limit=WIDTH-365

x_random=np.arange(left_x_limit,right_x_limit,50)

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
        sound_accelerate.play()
        self.vel = min(self.vel + self.acceleration, self.max_vel)

    def movement(self,left=False,right=False):
        if left:
            horizontal = self.vel
            self.x -= horizontal
        elif right:
            horizontal = self.vel
            self.x += horizontal

        # check boundary (west)
        if self.x < left_x_limit:
           self.x = left_x_limit
       # check boundary (east)
        if self.x > right_x_limit:
           self.x = right_x_limit

    def reduce_speed(self):
        self.vel = max(self.vel - self.acceleration , 0)
    

def score_board(dodged):
    global font1
    text = font1.render('Dodged: ' + str(dodged),True,(0,0,0))
    WIN.blit(text,(0,0)) 
    pygame.display.update()

def speedometer(velocity):
    global font1
    text = font1.render(str(round(velocity,1))+"  KMPH",True,(0,0,0))
    WIN.blit(SPEEDOMETER,(0,155))
    WIN.blit(text,(60,145))
    pygame.display.update()

class PlayerCar(AbstractCar):
    IMG = RED_CAR
    START_POS = (5*HEIGHT/6, WIDTH-450)

# class to make arbitary vehicles
class Block():
    def __init__(self,x,y,vel):
        self.image=GREEN_CAR
        self.vehicle_number=0
        self.x = x
        self.width=GREEN_CAR.get_width()
        self.height=GREEN_CAR.get_height()
        self.y = y
        self.speedy = vel
        self.acceleration = 0.1
        self.dodged = 0
        self.min_velocity=3
        
    def update(self,vel,random_coordinate):
        self.speedy=max(vel + self.acceleration, self.min_velocity)
        self.y = self.y + self.speedy
       # check boundary (block)
        if self.y > WIDTH:
            self.y = 0 - 10 # choosing randomly x coordinate
            self.x = random_coordinate
            #print(self.x,left_x_limit,right_x_limit-self.width)
            self.dodged = self.dodged + 2
            self.vehicle_number=random.randint(0,len(all_vehicles)-1)
            self.image = scale_image(pygame.image.load("images/"+all_vehicles[self.vehicle_number]), 0.55)
            self.width=self.image.get_width()
            self.height=self.image.get_height()

    def draw(self,wn):
        # pygame.draw.rect(wn, (255,0,0), [self.x, self.y, self.width, self.height])
        wn.blit(self.image,(self.x,self.y))

    def collison(self,mask,x,y):
        obstacle_mask = pygame.mask.from_surface(self.image)
        offset = (int(self.x - x), int(self.y - y))
        poi = mask.overlap(obstacle_mask, offset)
        if poi != None:
            sound_accelerate.set_volume(0)
            sound=pygame.mixer.Sound("sounds/car-crash-sound-eefect.mp3")
            sound.set_volume(0.8)
            sound.play()
            text = font1.render('You crashed!',True,(0,0,0))
            text_width = text.get_width()
            text_height = text.get_height()
            x = int(WIDTH/2-text_width/2)
            y = int(HEIGHT/2-text_height/2)
            WIN.blit(text,(x,y))
            WIN.blit(CRASH,(player_car.x-100,player_car.y-100))
            pygame.display.update()
            time.sleep(1)
            return True
        return False


run = True
clock = pygame.time.Clock()
player_car = PlayerCar(INITIAL_VELOCITY, 4)

block_x=random.choices(np.arange(left_x_limit, right_x_limit+1),k=5)

block1_x = block_x[0]
block1_y = -100

block2_x =block_x[1]
block2_y = -50

block1 = Block(block1_x,block1_y,player_car.vel)
block2 = Block(block2_x,block2_y,player_car.vel)
movement_in_y = 0
while run:
    clock.tick(FPS)

    # to genrate random coordinates everytime for obstacles
    list1=x_random.tolist()
    list1.remove(list1[0])
    x_random2=random.choices(list1,k=1)

    block1.update(player_car.vel,x_random[0])
    block2.update(player_car.vel,x_random2[0])

    # displaying grass road and car
    WIN.blit(GRASS,(0,movement_in_y))
    WIN.blit(GRASS,(0,movement_in_y-GRASS.get_height()))

    # to move and display the road
    WIN.blit(TRACK,(0,movement_in_y))
    WIN.blit(TRACK,(0,movement_in_y-TRACK.get_height()))
    movement_in_y+=player_car.vel
    if (TRACK.get_height()-int(movement_in_y))<=11:
        WIN.blit(GRASS,(0,movement_in_y-GRASS.get_height()))
        WIN.blit(TRACK,(0,movement_in_y-TRACK.get_height()))
        movement_in_y=0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            break

    player_car.draw(WIN)
    block1.draw(WIN)
    block2.draw(WIN)


    keys = pygame.key.get_pressed()
    moved = False

    if keys[pygame.K_a] or keys[pygame.K_LEFT]:
        player_car.movement(left=True)
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        player_car.movement(right=True)
    moved = True
    player_car.move_forward()

    if not moved or keys[pygame.K_DOWN] or keys[pygame.K_SPACE]:
        player_car.reduce_speed()
    
    # Car collision with block pixel perfect coollision
    player_car_mask=pygame.mask.from_surface(player_car.img)
    collided = 0
    if(block1.collison(player_car_mask,player_car.x,player_car.y)):
        collided = 1
    if(block2.collison(player_car_mask,player_car.x,player_car.y)):
        collided = 1
    if collided:
        run = True
        clock = pygame.time.Clock()
        player_car = PlayerCar(INITIAL_VELOCITY, 4)

        block_x=random.choices(np.arange(left_x_limit, right_x_limit+1),k=5)

        block1_x = block_x[0]
        block1_y = -100

        block2_x =block_x[1]
        block2_y = -50

        block1 = Block(block1_x,block1_y,player_car.vel)
        block2=Block(block2_x,block2_y,player_car.vel)
        movement_in_y=0


    # Score
    score_board(block1.dodged+block2.dodged)
    speedometer(player_car.vel)
    player_car.max_vel = INITIAL_VELOCITY+((block1.dodged+block2.dodged)//50)*2
    pygame.display.update()


pygame.quit()
