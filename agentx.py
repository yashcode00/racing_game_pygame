import random
import numpy as np
from main import PlayerCarAI
from cnn_model import Agent
import cv2
import matplotlib.pyplot as plt
from IPython import display

plt.ion()

def plot(scores, mean_scores):
    display.clear_output(wait=True)
    display.display(plt.gcf())
    plt.clf()
    plt.title('Training...')
    plt.xlabel('Number of Games')
    plt.ylabel('Score')
    plt.plot(scores)
    plt.plot(mean_scores)
    plt.ylim(ymin=0)
    plt.text(len(scores)-1, scores[-1], str(scores[-1]))
    plt.text(len(mean_scores)-1, mean_scores[-1], str(mean_scores[-1]))
    plt.show(block=False)
    plt.pause(.1) 

lr=0.00001
gamma=0.99
epsilon=1.0
batch_size=64
mem_size=3000

def preprocess(frame):
    frame=cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    frame=cv2.resize(frame, (80,80))
    frame=frame/255
    return frame

def stack_frames(stacked_frames,frame, stack_size):
    if stacked_frames is None:
        stacked_frames = np.zeros((*frame.shape, stack_size))
        actions = np.zeros(stack_size)
        for idx in range(stack_size):
            stacked_frames[:,:,idx] = frame
    else:
        stacked_frames[:,:,0:stack_size-1] = stacked_frames[:,:,1:]
        stacked_frames[:,:,stack_size-1] = frame
    return stacked_frames

def train():
    played=0
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    stack_size=4
    scores=[]
    numGames=2000
    record = 0
    agent = Agent(lr,gamma,mem_size,3,epsilon,batch_size)
    game = PlayerCarAI()
    print("Loading up the agent's memory with random gameplay")
    while agent.mem_cntr<25000:
        done = False
        observation = game.reset()
        observation = preprocess(observation)
        stacked_frames = None
        observation = stack_frames(stacked_frames, observation, stack_size)
        while not done:
            action = np.random.choice([0, 1, 2])
            action += 1
            observation_, reward, done, info = game.step(action)
            observation_ = stack_frames(stacked_frames,
                                        preprocess(observation_), stack_size)
            action -= 1
            agent.store_transition(observation, action,
                                    reward, observation_, int(done))
            observation = observation_
        # storing and plotting scores vs no_games
        played+=1
        if info>record:
            record=info
        plot_scores.append(info)
        total_score+=info
        plot_mean_scores.append(total_score/played)
        plot(plot_scores,plot_mean_scores)
        print("Game: ",played," Score: ",info," Record: ",record)


    print("Done with random gameplay. Game on.")

    n_steps = 0
    for i in range(numGames):
        done = False
        observation = game.reset()
        observation = preprocess(observation)
        stacked_frames = None
        observation = stack_frames(stacked_frames, observation, stack_size)
        score = 0
        while not done:
            action = agent.choose_action(observation)
            observation_, reward, done, info = game.step(action)
            observation_ = stack_frames(stacked_frames,
                                        preprocess(observation_), stack_size)
            agent.store_transition(observation, action,
                                   reward, observation_, int(done))
            observation = observation_
            agent.learn()

        # storing and plotting scores vs no_games
        played+=1
        if info>record:
            record=info
        plot_scores.append(info)
        total_score+=info
        plot_mean_scores.append(total_score/played)
        plot(plot_scores,plot_mean_scores)
        print("Game: ",played," Score: ",info," Record: ",record)

        if i % 12 == 0 and i > 0:
            # avg_score = np.mean(scores[max(0, i-12):(i+1)])
            # print('episode: ', i,'score: ', score,
            #      ' average score %.3f' % avg_score,
            #     'epsilon %.3f' % agent.epsilon)
            agent.save_models()
        # else:
        #     print('episode: ', i,'score: ', score)
        # # eps_history.append(agent.epsilon)
        # scores.append(score)
        # x = [i+1 for i in range(numGames)]
        # plotLearning(x, scores)

        # if done:
        #     agent.n_games += 1
        #     # agent.train_long_memory()

        #     if score > record:
        #         record = score
        #         agent.model.save()

        #     print('Game', agent.n_games, 'Score', score, 'Record:', record)

        #     plot_scores.append(score)
        #     total_score += score
        #     mean_score = total_score / agent.n_games
        #     plot_mean_scores.append(mean_score)
        #     plot(plot_scores, plot_mean_scores)


if __name__ == '__main__':
    train()