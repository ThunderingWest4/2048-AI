import tensorflow.keras as keras
from tensorflow.keras.layers import *
from tensorflow.keras.initializers import *
import tensorflow as tf
import numpy as np
from collections import deque

"""
ADD EXPERIENCE REPLAY (LEARNING FROM PAST MOVES), ACTIONS, AND HOOK IT UP TO WORKING 2048
ALSO GET SLOWLY DECREASING EPSILON AND GRAPH THE GAME SCORE OVER TIME
"""

class DQNAgent():
    def __init__(self, state_dim: tuple, action_dim: int, dqsize: int, eps_init: int, min_eps: int, max_eps: int, eps_decay: int):
        """
        :param tuple state_dim: a tuple with the (xdim, ydim) of the board
        :param int action_dim: an int with the possible actions, 4 in the case of 2048
        :param int dqsize: an int as the size of the deque for the environment replay
        :param int eps_init: an int representing the initial epsilon value
        :param int min_eps: an int representing the minimum epsilon value (randomness in action)
        :param int max_eps: an int representing the maximum epsilon
        :param int eps_decay: the rate at which the epsilon decays
        """
        self.state = state_dim
        self.action = action_dim
        self.dqlen = dqsize
        self.construct_net(0.001)
        self.eps = eps_init
        self.emax = max_eps
        self.emin = min_eps
        self.edecay = eps_decay
        

    def construct_net(self, lr):

        layer_dims = [(16,), 24, 12, 4]

        self.net = keras.Sequential()
        init = keras.initializers.he_normal()
        self.net.add(keras.layers.Dense(
            24, input_shape=layer_dims[0], activation='relu', kernel_initializer=init
        )) 
        for x in layer_dims[2:-1]:
            self.net.add(keras.layers.Dense(x, activation='relu', kernel_initializer=init))

        self.net.add(keras.layers.Dense(layer_dims[-1], activation='linear', kernel_initializer=init))
        
        # self.net = keras.Sequential(dense_layers + [q_vals])
        self.net.compile(
            optimizer=keras.optimizers.Adam(learning_rate=lr),
            loss=tf.keras.losses.Huber(), 
            metrics=['accuracy']
        )

        self.net.summary()

        # inp = Input(shape=self.state)
        # hidden1 = Dense(
        #     25, activation="relu", kernel_initializer=he_normal()
        # )(inp)
        # hidden2 = Dense(
        #     25, activation="relu", kernel_initializer=he_normal()
        # )(hidden1)
        # hidden3 = Dense(
        #     25, activation="relu", kernel_initializer=he_normal()
        # )(hidden2)
        # q_values = Dense(
        #     self.action, kernel_initializer=Zeros(), activation="linear"
        # )(hidden3)

        # self.net = keras.Model(inputs=inp, outputs=[q_values])

        # self.net.compile(loss=tf.keras.losses.Huber(), optimizer=tf.keras.optimizers.Adam(lr=lr), metrics=['accuracy'])

    def act(self, state):
        s = self.convertState(state)

        re_s = s.reshape([1, s.shape[0]])
        pred_distr = self.net.predict(re_s)[0]

        return np.argmax(pred_distr)

    def convertState(self, s):
        # convert the state array from an array of custom cell/void items to an array of numbers readable by tensorflow
        a = np.array([np.array(x) for x in s]) # converting s into a bunch of np.arrays
        b = a.flatten() # flatten a to 1D
        c = np.array([x.val for x in b]) # convert from my custom classes to nums
        return c

    def get_qs(model, state):
        return model.predict(state)[0]

    def train(env, replay_memory, model, target_model, done):
        learning_rate = 0.7 # Learning rate
        discount_factor = 0.618

        MIN_REPLAY_SIZE = 1000
        if len(replay_memory) < MIN_REPLAY_SIZE:
            return

        batch_size = 64 * 2
        mini_batch = np.random.sample(replay_memory, batch_size)
        current_states = np.array([transition[0] for transition in mini_batch])
        current_qs_list = model.predict(current_states)
        new_current_states = np.array([transition[3] for transition in mini_batch])
        future_qs_list = target_model.predict(new_current_states)

        X = []
        Y = []
        for index, (observation, action, reward, new_observation, done) in enumerate(mini_batch):
            if not done:
                max_future_q = reward + discount_factor * np.max(future_qs_list[index])
            else:
                max_future_q = reward

            current_qs = current_qs_list[index]
            current_qs[action] = (1 - learning_rate) * current_qs[action] + learning_rate * max_future_q

            X.append(observation)
            Y.append(current_qs)

        model.fit(np.array(X), np.array(Y), batch_size=batch_size, verbose=0, shuffle=True)

    def updateEps(self, episode: int):
        self.eps = self.emin + (self.emax - self.emin) * np.exp(-self.edecay * episode)