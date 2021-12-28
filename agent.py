import tensorflow.keras as keras
from tensorflow.keras.layers import *
from tensorflow.keras.initializers import *
import tensorflow as tf
import numpy as np
from collections import deque
import random

# ACTOR-CRITIC DQN DIDNT END UP WORKING OUT SO LETS TRY CONVOLUTIONS
# BASED OFF OF A DQN ARCHITECTURE FROM UWATERLOO https://cs.uwaterloo.ca/~mli/zalevine-dqn-2048.pdf

class CNNAgent():
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
        self.exps = deque(maxlen=dqsize)
        self.eps = eps_init
        self.emax = max_eps
        self.emin = min_eps
        self.edecay = eps_decay

        self.discount = 0.618
        self.lr = 0.01

        self.construct_net()
        
    def construct_net(self):

        self.net = keras.Sequential()
        init = keras.initializers.he_normal()
        self.net.add(
            Conv2D(input_shape=(4,4,16), strides=1, padding="SAME", filters=256, activation='relu', kernel_size=2)
        )

        for i in range(3):
            self.net.add(
                Conv2D(strides=1, padding="SAME", filters=256, activation='relu', kernel_size=2)
            )

        self.net.add(
            Conv2D(strides=1, padding="SAME", filters=4, activation='relu', kernel_size=2)
        )

        self.net.add(
            keras.layers.Dense(4, activation='softmax', kernel_initializer=init)
        )
        
        # self.net = keras.Sequential(dense_layers + [q_vals])
        self.net.compile(
            optimizer=keras.optimizers.Adam(learning_rate=self.lr),
            loss=tf.keras.losses.Huber(),
            metrics=['accuracy']
        )

        self.net.summary()

    def act(self, state):
        s = self.convertState(state)

        re_s = s.reshape([1, s.shape[0]])
        pred_distr = self.chef.predict(re_s)[0]

        return np.argmax(pred_distr)

    def convertState(self, s):
        # convert the state array from an array of custom cell/void items to an array of numbers readable by tensorflow
        a = np.array([np.array([y.val for y in x]) for x in s]) # converting s into a bunch of np.arrays
        
        # now converting into the 4x4x16 channels for conv2d
        # current shape is 32x4x4
        return a

    def collect_exp(self, vals):
        self.exps.append(vals)

    def get_qs(model, state):
        return model.predict(state)[0]

    def train(self, batch_size):
        # getting random samples
        samples = random.sample(self.exps, batch_size)
        
        xs, ys = [], []

        cur_states = np.array([x[0] for x in samples])
        current_qs = self.net.predict(cur_states)
        new_states = np.array([x[3] for x in samples])
        future_qs = self.net.predict(new_states)

        for idx, (cur, action, rew, s_next, done) in enumerate(samples):
            """
            formatting for each sample: 
            [current state, action taken, reward from current SA, next state, done]
            """

            if not done:
                max_q = rew + self.discount*np.max(future_qs[idx])
            else:
                max_q = rew

            cur_q = current_qs[idx]
            current_qs[action] = (1-self.lr)*current_qs[action] + self.lr*max_q


            xs.append(cur)
            ys.append(current_qs)


        self.net.fit(
            np.array(xs), np.array(ys), 
            epochs=1, 
            batch_size=batch_size,
            shuffle=True,
            verbose=0,
            use_multiprocessing=True,
            workers=16
        )

        return 0

    def updateEps(self, episode: int):
        self.eps = self.emin + (self.emax - self.emin) * np.exp(-self.edecay * episode)


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
        self.exps = deque(maxlen=dqsize)
        self.eps = eps_init
        self.emax = max_eps
        self.emin = min_eps
        self.edecay = eps_decay

        self.discount = 0.618
        self.lr = 0.01

        # reason behind this naming:
        # instead of actor-critic, i did chef-critic
        # because i love the image of a chef frantically
        # trying to cook in a kitchen while a critic is in the back
        # yelling at him to do better
        self.chef = self.construct_net(self.lr)
        self.critic = self.construct_net(self.lr)
        self.copy_weights()

        
    def construct_net(self, lr):

        layer_dims = [(16,), 52, 36, 24, 4]

        net = keras.Sequential()
        init = keras.initializers.he_normal()
        net.add(keras.layers.Dense(
            24, input_shape=layer_dims[0], activation='relu', kernel_initializer=init
        )) 
        for x in layer_dims[2:-1]:
            net.add(keras.layers.Dense(x, activation='relu', kernel_initializer=init))

        net.add(keras.layers.Dense(layer_dims[-1], activation='linear', kernel_initializer=init))
        
        # self.net = keras.Sequential(dense_layers + [q_vals])
        net.compile(
            optimizer=keras.optimizers.Adam(learning_rate=lr),
            loss=tf.keras.losses.Huber(), 
            metrics=['accuracy']
        )

        net.summary()

        return net

    def copy_weights(self):
        self.chef.set_weights(self.critic.get_weights())


    def act(self, state):
        s = self.convertState(state)

        re_s = s.reshape([1, s.shape[0]])
        pred_distr = self.chef.predict(re_s)[0]

        return np.argmax(pred_distr)

    def convertState(self, s):
        # convert the state array from an array of custom cell/void items to an array of numbers readable by tensorflow
        a = np.array([np.array(x) for x in s]) # converting s into a bunch of np.arrays
        b = a.flatten() # flatten a to 1D
        c = np.array([x.val for x in b]) # convert from my custom classes to nums
        return c

    def collect_exp(self, vals):
        self.exps.append(vals)

    def get_qs(model, state):
        return model.predict(state)[0]

    def train(self, batch_size):
        # getting random samples
        samples = random.sample(self.exps, batch_size)
        
        xs, ys = [], []

        cur_states = np.array([x[0] for x in samples])
        current_qs = self.chef.predict(cur_states)
        new_states = np.array([x[3] for x in samples])
        future_qs = self.critic.predict(new_states)

        for idx, (cur, action, rew, s_next, done) in enumerate(samples):
            """
            formatting for each sample: 
            [current state, action taken, reward from current SA, next state, done]
            """

            if not done:
                max_q = rew + self.discount*np.max(future_qs[idx])
            else:
                max_q = rew

            cur_q = current_qs[idx]
            current_qs[action] = (1-self.lr)*current_qs[action] + self.lr*max_q


            xs.append(cur)
            ys.append(current_qs)


        self.critic.fit(
            np.array(xs), np.array(ys), 
            epochs=1, 
            batch_size=batch_size,
            shuffle=True,
            verbose=0,
            use_multiprocessing=True,
            workers=16
        )

        return 0

    def updateEps(self, episode: int):
        self.eps = self.emin + (self.emax - self.emin) * np.exp(-self.edecay * episode)