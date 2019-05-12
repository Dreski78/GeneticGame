import keras
import numpy as np
import gym
import random
from statistics import median, mean
from collections import Counter
import matplotlib.pyplot as plt
from keras.engine.saving import load_model
from keras.models import Model
from keras.layers import Input, Dense



# env = gym.make("CartPole-v0")
from Game_AI import Game

env = Game()
env.reset()
goal_steps = 100
score_requirement = 5
initial_games = 10000


def initial_population():
    # [OBS, MOVES]
    training_data = []
    # all scores:
    scores = []
    # just the scores that met our threshold:
    accepted_scores = []
    # iterate through however many games we want:
    for i in range(initial_games):
        score = 0
        # moves specifically from this environment:
        game_memory = []
        # previous observation that we saw
        prev_observation = []
        # for each frame in 200
        for j in range(goal_steps):
            # choose random action (0 or 1)
            action = random.randrange(0, 5)
            # do it!
            observation, reward, done, info = env.step(action)

            # notice that the observation is returned FROM the action
            # so we'll store the previous observation here, pairing
            # the prev observation to the action we'll take.
            if len(prev_observation) > 0:
                game_memory.append([prev_observation, action])
            prev_observation = observation
            score += reward
            if done:
                break

        # IF our score is higher than our threshold, we'd like to save
        # every move we made
        # NOTE the reinforcement methodology here.
        # all we're doing is reinforcing the score, we're not trying
        # to influence the machine in any way as to HOW that score is
        # reached.
        if score >= score_requirement:
            accepted_scores.append(score)
            for data in game_memory:
                # convert to one-hot (this is the output layer for our neural network)
                if data[1] == 0:
                    output = [1, 0, 0, 0, 0]
                elif data[1] == 1:
                    output = [0, 1, 0, 0, 0]
                elif data[1] == 2:
                    output = [0, 0, 1, 0, 0]
                elif data[1] == 3:
                    output = [0, 0, 0, 1, 0]
                elif data[1] == 4:
                    output = [0, 0, 0, 0, 1]

                # saving our training data
                training_data.append([data[0], output])

        # reset env to play again
        env.reset()
        # save overall scores
        scores.append(score)
        if i % 1000 == 0:
            print(f"{i//1000}/{initial_games//1000}")

    # just in case you wanted to reference later
    training_data_save = np.array(training_data)
    np.save('saved.npy', training_data_save)

    # some stats here, to further illustrate the neural network magic!
    plt.plot(accepted_scores, "o")
    plt.show()
    print('Average accepted score:', mean(accepted_scores))
    print('Median score for accepted scores:', median(accepted_scores))
    print(len(accepted_scores))

    return training_data

def neural_network_model():
    inputs = Input(shape=(5,))

    # a layer instance is callable on a tensor, and returns a tensor
    x = Dense(10, activation='relu')(inputs)
    x = Dense(5, activation='relu')(x)
    predictions = Dense(5, activation='softmax')(x)

    # This creates a model that includes
    # the Input layer and three Dense layers
    model = Model(inputs=inputs, outputs=predictions)
    opti = keras.optimizers.Adam(lr=0.005)
    loss = "categorical_crossentropy"
    model.compile(optimizer=opti,
                  loss=loss,
                  metrics=['accuracy'])
    return model


def train_model(training_data, model=False):
    # print(training_data[0][0])
    X = np.array([i[0] for i in training_data])

    Y = np.array([i[1] for i in training_data])

    if not model:
        model = neural_network_model()

    model.fit(X, Y, epochs=10, batch_size=1280, shuffle=True)
    return model


if __name__ == '__main__':
    train = initial_population()
    model = train_model(train)
    model.save('my_model1.h5')
    # model = load_model('my_model.h5')

    amt_games = 1000
    scores = []
    choices = []
    adv_scores = []
    steps = []

    for game in range(amt_games):
        score = 0
        game_memory = []
        prev_obs = []
        env.reset()
        for step in range(goal_steps):
            if len(prev_obs) == 0:
                action = random.randint(0, 5)
            else:
                action = np.argmax(model.predict(prev_obs.reshape(1, 5))[0])

            choices.append(action)
            observation, reward, done, info = env.step(action)
            prev_obs = np.array(observation)
            score += reward
            if done:
                scores.append(score)
                steps.append(step)
                break

        if game % 10 == 0 and game != 0:
            print(f"ep: {game}/{amt_games}")
    print('Average Score:', sum(scores) / len(scores))
    plt.plot(scores, "o")
    plt.show()


