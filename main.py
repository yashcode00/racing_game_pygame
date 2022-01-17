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

#TRACK_BORDER = scale_image(pygame.image.load("imgs/track-border.png"), 0.9)

RED_CAR = scale_image(pygame.image.load("images/main_agent2.png"), 0.55)
GREEN_CAR = scale_image(pygame.image.load("images/police.png"), 0.55)
TRUCK=scale_image(pygame.image.load("images/truck.png"), 0.55)

# WIDTH, HEIGHT = TRACK.get_width(), TRACK.get_height()
WIDTH, HEIGHT = GRASS.get_width(), GRASS.get_height()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Racing Game!")

FPS = 60

# setting the path limits
left_x_limit=260
right_x_limit=WIDTH-365

x_random=np.arange(left_x_limit,right_x_limit,50)    

class PlayerCarAI():
    def __init__(self, max_vel=20):
        # player car attributes
        self.img = RED_CAR
        self.max_vel = max_vel
        self.vel = 0
        self.x, self.y = (5*HEIGHT/6, WIDTH-450)
        self.acceleration = 0.1
        self.score=0
        self.game_over=False
        self.direction=[0,0,0]

        # 2 obstacles -> attributes start
        x_random=np.arange(left_x_limit,right_x_limit,50)
        list1=x_random.tolist()
        list1.remove(list1[0])
        x_random2=random.choices(list1,k=1)

        self.x1=x_random[0]
        self.x2=x_random2[0]
        self.y1=-100
        self.y2=-120
        self.v1=3
        self.v2=3
        self.min_velocity=3
        self.acceleration = 0.1

        self.image1=GREEN_CAR
        self.image2=TRUCK
        self.vehicle_number=[]

        self.dodged = 0

    def reset(self):
        self.__init__()

    def draw_player(self,win):
        win.blit(self.img,(self.x,self.y))
    
    # playet car methods->>>
    def move_forward(self):
        self.max_vel = self.max_vel+(self.dodged//10)*2
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

    
    def player_step(self,action):
        self.update()
        self.score_board()

        self.direction=action
        if action[1]:
            self.movement(left=True)
        elif action[2]:
            self.movement(right=True)

        # keep increasing speed
        self.move_forward()


        # now updating the scorecard and reward
        reward=0
        
        if self.game_over:
            reward = -10
        else :  # give reward when dodged count increases
            reward = 10

         # Score
        self.score=self.dodged
        self.speedometer()

        print("Reward: ",reward,",Score: ",self.score,",Game_Over: ",self.game_over)
        return reward,self.score, self.game_over


    

    # obstacles methods start->>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    def update(self):
        self.v1=max(self.vel + self.acceleration, self.min_velocity)
        self.y1 = self.y1 + self.v1
        # for second obstacle
        self.v2=max(self.vel + self.acceleration, self.min_velocity)
        self.y2 = self.y2 + self.v2

        # choosing random coordinate and random cars
        x_random=np.arange(left_x_limit,right_x_limit,80)
        list1=x_random.tolist()
        list1.remove(list1[0])
        x_random2=random.choices(list1,k=1)

        self.vehicle_number=random.sample(range(0,len(all_vehicles)-1),k=2)

       # check boundary (block) for obstacle 1
        if self.y1 > WIDTH:
            self.y1 = 0 - 10 # choosing randomly x coordinate
            self.x1 = x_random[0]
            #print(self.x,left_x_limit,right_x_limit-self.width)
            self.dodged = self.dodged + 2
            self.image1 = scale_image(pygame.image.load("images/"+all_vehicles[self.vehicle_number[0]]), 0.55)

        # check boundary (block) for obstacle 2
        if self.y2 > WIDTH:
            self.y2 = 0 - 20 # choosing randomly x coordinate
            self.x2 = x_random2[0]
            #print(self.x,left_x_limit,right_x_limit-self.width)
            self.dodged = self.dodged + 2
            self.image2 = scale_image(pygame.image.load("images/"+all_vehicles[self.vehicle_number[1]]), 0.55)


    def draw(self,win):
        win.blit(self.image1,(self.x1,self.y1))
        win.blit(self.image2,(self.x2,self.y2))

    def collison(self):
        obstacle1_mask = pygame.mask.from_surface(self.image1)
        offset1 = (int(self.x1 - self.x), int(self.y1 - self.y))

        obstacle2_mask = pygame.mask.from_surface(self.image2)
        offset2 = (int(self.x2 - self.x), int(self.y2 - self.y))
        
        # mask of player car
        mask=pygame.mask.from_surface(self.img)

        # now finding point of intersection
        poi1 = mask.overlap(obstacle1_mask, offset1)
        poi2 = mask.overlap(obstacle2_mask, offset2)
        if poi1 != None:
            sound=pygame.mixer.Sound("sounds/car-crash-sound-eefect.mp3")
            sound.set_volume(0.8)
            sound.play()
            text = font1.render('You crashed!',True,(0,0,0))
            text_width = text.get_width()
            text_height = text.get_height()
            x = int(WIDTH/2-text_width/2)
            y = int(HEIGHT/2-text_height/2)
            WIN.blit(text,(x,y))
            WIN.blit(CRASH,(self.x-100,self.y-100))
            pygame.display.update()
            time.sleep(1)
            return True

        # checking collision for second car
        if poi2 != None:
            sound=pygame.mixer.Sound("sounds/car-crash-sound-eefect.mp3")
            sound.set_volume(0.8)
            sound.play()
            text = font1.render('You crashed!',True,(0,0,0))
            text_width = text.get_width()
            text_height = text.get_height()
            x = int(WIDTH/2-text_width/2)
            y = int(HEIGHT/2-text_height/2)
            WIN.blit(text,(x,y))
            WIN.blit(CRASH,(self.x-100,self.y-100))
            pygame.display.update()
            time.sleep(1)
            return True
        
        return False
        
    def score_board(self):
        global font1
        text = font1.render('Dodged: ' + str(self.dodged),True,(0,0,0))
        WIN.blit(text,(0,0)) 
        pygame.display.update()

    def speedometer(self):
        global font1
        text = font1.render(str(round(self.vel,1))+"  KMPH",True,(0,0,0))
        WIN.blit(SPEEDOMETER,(0,155))
        WIN.blit(text,(60,145))
        pygame.display.update()



run = True
clock = pygame.time.Clock()
player_car = PlayerCarAI()
movement_in_y=0

while run:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            break

    indx=np.random.randint(0,3)
    action=[0,0,0]
    action[indx]=1

    clock.tick(FPS)

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

    player_car.draw_player(WIN)
    player_car.draw(WIN)

    player_car.player_step(action)

    if player_car.game_over:
        player_car.reset()

    if(player_car.collison()):
        player_car.game_over=True

    pygame.display.update()


pygame.quit()
