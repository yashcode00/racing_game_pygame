from os import stat
import torch
import random
import numpy as np
from collections import deque
from main import HEIGHT, WIDTH, PlayerCarAI, left_x_limit, right_x_limit
from model import Linear_QNet, QTrainer
from plot_it import plot
import torchvision.transforms as tt
from PIL import Image
from collections import Counter

MAX_MEMORY = 100000
BATCH_SIZE = 1000
LR = 0.001

class Agent:

    def __init__(self):
        self.n_games = 0
        self.epsilon = 0 # randomness
        self.gamma = 0.9 # discount rate
        self.memory = deque(maxlen=MAX_MEMORY) # popleft()
        self.model = Linear_QNet(3, 3)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)


    def get_state(self, game):

        # dir_l = game.direction == [0,1,0]
        # dir_r = game.direction == [0,0,1]
        # dir_u = game.direction == [1,0,0]

        # state_img=Image.open("State/state.png").convert('RGB')
        # state_img=transforms_test(state_img)
        # print(state_img.shape)

        # state = [
        #     # Move direction
        #     dir_l,
        #     dir_r,
        #     dir_u
        #     # obstacle coordinate
        #     ]


        # return np.array(state, dtype=int)

        if len(game.state_np)<4:
            return torch.from_numpy(np.zeros(shape=(1,3,64,64)))
        return game.state

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done)) # popleft if MAX_MEMORY is reached

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE) # list of tuples
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)
        #for state, action, reward, nexrt_state, done in mini_sample:
        #    self.trainer.train_step(state, action, reward, next_state, done)

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self, state):
        # random moves: tradeoff exploration / exploitation
        self.epsilon = 80 - self.n_games
        final_move = [0,0,0]
        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 2)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            #print(prediction)
            a=[0,0,0]
            for val in prediction:
                a[torch.argmax(val)]+=1
            #print(a)
            move=np.argmax(a)
            #print(move)
            #move = torch.argmax(prediction).item()
            final_move[move] = 1

        return final_move


def train():
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    agent = Agent()
    game = PlayerCarAI()
    while True:
        if game.calls>3:
            # get old state
            state_old = agent.get_state(game)

            # get move
            final_move = agent.get_action(state_old)
            #print("Here")

            # perform move and get new state
            reward, done, score = game.player_step(final_move)
            state_new = agent.get_state(game)

            # train short memory
            agent.train_short_memory(state_old, final_move, reward, state_new, done)

            # remember
            agent.remember(state_old, final_move, reward, state_new, done)

            if done:
                # train long memory, plot result
                game.reset()
                agent.n_games += 1
                agent.train_long_memory()

                if score > record:
                    record = score
                    agent.model.save()

                print('Game', agent.n_games, 'Score', score, 'Record:', record)

                plot_scores.append(score)
                total_score += score
                mean_score = total_score / agent.n_games
                plot_mean_scores.append(mean_score)
                plot(plot_scores, plot_mean_scores)
        else:
            game.player_step()


if __name__ == '__main__':
    train()