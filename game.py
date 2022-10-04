from gym import Env
from gym.spaces import Discrete, Box
import numpy as np
import random
import pygame
import time
import math
import random
import os
import numpy as np
from collections import deque
from PIL import Image
import cv2
from io import BytesIO
import torch

pygame.init()
font1 = pygame.font.Font('freesansbold.ttf', 32)
MAX_MEMORY = 100_000

from pygame.constants import HIDDEN

def scale_image(img, factor):
    size = round(img.get_width() * factor), round(img.get_height() * factor)
    return pygame.transform.scale(img, size)


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
pygame.display.set_caption("Racing Game!")

FPS = 60

# setting the path limits
left_x_limit=260
right_x_limit=WIDTH-365

x_random=np.arange(left_x_limit,right_x_limit,50)   

class CustomEnv(Env):
    def __init__(self, max_vel=10):
        super(CustomEnv, self).__init__()
        self.WIN = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.mixer.init()
        # player car attributes
        self.img = RED_CAR
        self.initial_vel=10
        self.max_vel = max_vel
        self.vel = 0
        self.x, self.y = (5*HEIGHT/6, WIDTH-450)
        self.acceleration = 0.07
        self.score=0
        self.game_over=False
        self.direction=[0,0,0]
        self.rect = pygame.Rect(left_x_limit-10, 0, right_x_limit-left_x_limit+70,HEIGHT)
       
        # 2 obstacles -> attributes start
        x_random=np.arange(left_x_limit,right_x_limit,50)
        # list1=x_random.tolist()
        # list1.remove(list1[0])
        # x_random2=random.choices(list1,k=1)
        x_choices = set(x_random)
        x_blocks = random.sample(x_choices, 2)

        self.x1=x_blocks[0]
        self.x2=x_blocks[1]
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
        self.rewards=deque(maxlen=MAX_MEMORY)
        self.rewards.append(0)

        # surroundings movement
        self.movement_in_y=0
        self.state=torch.zeros([0])
        self.state_np=torch.from_numpy(np.zeros(shape=(1,3,64,64)))
        self.calls=0
        self.stacked_frames=4
        self.list_1=[]
        self.N_CHANNELS=3

        # Actions we can take, down, stay, up
        self.action_space = Discrete(3)
        # Temperature array
        self.observation_space = Box(low=0, high=255, shape=(3,64,64), dtype=np.uint8)
        # Set shower length
        self.length = 60
    
    def reset(self):
        self.__init__()
        return self.observation_space
    
    def draw_player(self,win):
        win.blit(self.img,(self.x,self.y))
    
    # playet car methods->>>
    def move_forward(self):
        self.max_vel = self.initial_vel+(self.dodged//30)*2
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
        
    def step(self, action):
        self.calls+=1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        
        if self.calls>4:
            # print("Deleted")
            self.list_1=self.list_1[1:]

        # Set placeholder for info
        info = {}
        frame = self.WIN.subsurface(self.rect)
        frame= pygame.image.tostring(frame, 'RGB')
        frame=pygame.image.fromstring(frame,(right_x_limit-left_x_limit+70,HEIGHT),'RGB')
        frame=pygame.surfarray.array3d(frame)
        frame=cv2.resize(frame, (64,64)).reshape(3,64,64)
        #print(frame.shape,",,,,",type(frame))
        self.list_1.append(frame)
        self.state_np=np.array(self.list_1)

        #print("Numpy shape:---->",self.state_np.shape)
        self.state=torch.from_numpy(self.state_np)
        # print("****************************",self.state.shape)


#         if self.calls<self.stacked_frames:
#             indx=np.random.randint(0,3)
#             action=[0,0,0]
#             action[indx]=1
#             self.direction=action
#             if action[1]==1:
#                 self.movement(left=True)
#             elif action[2]==1:
#                 self.movement(right=True)

#             # keep increasing speed
#             self.move_forward()
#             self.update_ui()
#             return 0, self.game_over,self.score

        

        #pygame.image.save(sub,"State/state.png")
        #self.state=cv2.cvtColor(self.state, cv2.COLOR_BGR2GRAY)
        #print(self.state.shape)
        
        # self.state=np.expand_dims(self.state, axis=0)
        # self.state=self.state.flatten()/255
        # print(self.state.shape)
        self.direction=action
        if action==1:
            self.movement(left=True)
        elif action==2:
            self.movement(right=True)

        # keep increasing speed
        self.move_forward()
        self.update()
        self.update_ui()

        # now updating the scorecard and reward
        reward=0
        
        if self.game_over or self.length <= 0:
            reward = -10
        else:  # give reward when dodged count increases
            reward = self.rewards.pop()

         # Score
        self.score=self.dodged
        #print("Reward: ",reward,",Score: ",self.score,",Game_Over: ",self.game_over)
             # Return step information
        return np.array(frame), reward, self.game_over, info
    
    # obstacles methods start->>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    def update(self):
        flag=0
        self.v1=max(self.vel + self.acceleration, self.min_velocity)
        self.y1 = self.y1 + self.v1
        # for second obstacle
        self.v2=max(self.vel + self.acceleration, self.min_velocity)
        self.y2 = self.y2 + self.v2

        # choosing random coordinate and random cars
        x_random=np.arange(left_x_limit,right_x_limit,50)
        # list1=x_random.tolist()
        # list1.remove(list1[0])
        # x_random2=random.choices(list1,k=1)
        x_choices = set(x_random)
        x_blocks = random.sample(x_choices, 2)

        self.vehicle_number=random.sample(range(0,len(all_vehicles)-1),k=2)

       # check boundary (block) for obstacle 1
        if self.y1 > WIDTH:
            self.y1 = 0 - 10 # choosing randomly x coordinate
            if self.x2 == x_blocks[0]:
                possible_choices = [v for v in x_random if v != x_blocks[0]]
                x_blocks[0] = random.choice(possible_choices)

            self.x1 = x_blocks[0]
            #print(self.x,left_x_limit,right_x_limit-self.width)
            self.dodged = self.dodged + 2
            self.image1 = scale_image(pygame.image.load("images/"+all_vehicles[self.vehicle_number[0]]), 0.55)
            self.rewards.append(10)
            flag=1

        # check boundary (block) for obstacle 2
        if self.y2 > WIDTH:
            self.y2 = 0 - 20 # choosing randomly x coordinate
            if self.x1 == x_blocks[1]:
                possible_choices = [v for v in x_random if v != x_blocks[1]]
                x_blocks[1] = random.choice(possible_choices)
            self.x2 = x_blocks[1]
            #print(self.x,left_x_limit,right_x_limit-self.width)
            self.dodged = self.dodged + 2
            self.image2 = scale_image(pygame.image.load("images/"+all_vehicles[self.vehicle_number[1]]), 0.55)
            self.rewards.append(10)
            flag=1
            
        if(flag==0):
            self.rewards.append(0)
    def draw(self,win):
        win.blit(self.image1,(self.x1,self.y1))
        win.blit(self.image2,(self.x2,self.y2))

    def get_state(self,x,y):
        obstacle1_mask = pygame.mask.from_surface(self.image1)
        offset1 = (int(self.x1 - x), int(self.y1 - y))

        obstacle2_mask = pygame.mask.from_surface(self.image2)
        offset2 = (int(self.x2 - x), int(self.y2 - y))
        
        # mask of player car
        mask=pygame.mask.from_surface(self.img)

        # now finding point of intersection
        poi1 = mask.overlap(obstacle1_mask, offset1)
        poi2 = mask.overlap(obstacle2_mask, offset2)

        if poi1!=None or poi2!=None:
            return True
        
        return False

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
            # sound=pygame.mixer.Sound("sounds/car-crash-sound-eefect.mp3")
            # sound.set_volume(0.1)
            # sound.play()
            text = font1.render('You crashed!',True,(0,0,0))
            text_width = text.get_width()
            text_height = text.get_height()
            x = int(WIDTH/2-text_width/2)
            y = int(HEIGHT/2-text_height/2)
            self.WIN.blit(text,(x,y))
            self.WIN.blit(CRASH,(self.x-100,self.y-100))
            #pygame.display.update()
            #time.sleep(1)
            return True

        # checking collision for second car
        if poi2 != None:
            # sound=pygame.mixer.Sound("sounds/car-crash-sound-eefect.mp3")
            # sound.set_volume(0.1)
            # sound.play()
            text = font1.render('You crashed!',True,(0,0,0))
            text_width = text.get_width()
            text_height = text.get_height()
            x = int(WIDTH/2-text_width/2)
            y = int(HEIGHT/2-text_height/2)
            self.WIN.blit(text,(x,y))
            self.WIN.blit(CRASH,(self.x-100,self.y-100))
            # pygame.display.update()
            # time.sleep(1)
            return True
        
        return False
        
    def score_board(self):
        global font1
        text = font1.render('Dodged: ' + str(self.dodged),True,(0,0,0))
        self.WIN.blit(text,(0,0)) 

    def speedometer(self):
        global font1
        text = font1.render(str(round(self.vel,1))+"  KMPH",True,(0,0,0))
        self.WIN.blit(SPEEDOMETER,(0,155))
        self.WIN.blit(text,(60,145))

    def update_ui(self):
        clock.tick(FPS)

        # displaying grass road and car
        self.WIN.blit(GRASS,(0,self.movement_in_y))
        self.WIN.blit(GRASS,(0,self.movement_in_y-GRASS.get_height()))

        # to move and display the road
        self.WIN.blit(TRACK,(0,self.movement_in_y))
        self.WIN.blit(TRACK,(0,self.movement_in_y-TRACK.get_height()))

        self.movement_in_y+=self.vel

        if (TRACK.get_height()-int(self.movement_in_y))<=11:
            self.WIN.blit(GRASS,(0,self.movement_in_y-GRASS.get_height()))
            self.WIN.blit(TRACK,(0,self.movement_in_y-TRACK.get_height()))
            self.movement_in_y=0

        self.draw_player(self.WIN)
        self.draw(self.WIN)
        self.score_board()
        self.speedometer()

        if self.game_over:
            self.reset()

        if(self.collison()):
            self.game_over=True

        pygame.display.update()
        
            
            
    def render(self):
        # Implement viz
        pass

env=CustomEnv()


# In[ ]:


env.observation_space.sample()


# In[ ]:


clock = pygame.time.Clock()


# In[ ]:


# episodes = 10
# for episode in range(1, episodes+1):
#     state = env.reset()
#     done = False
#     score = 0 
    
#     while not done:
#         #env.render()
#         action = env.action_space.sample()
#         n_state, reward, done, info = env.step(action)
#         score+=reward
#     print('Episode:{} Score:{}'.format(episode, score))
# pygame.quit()
# quit()


# In[ ]:


states = env.observation_space.shape
actions = env.action_space.n


# In[ ]:


# In[ ]:


# In[ ]:


from stable_baselines import HER, SAC, PPO2, DQN


# In[ ]:


model=PPO2('MlpPolicy',env,verbose=1)

# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




