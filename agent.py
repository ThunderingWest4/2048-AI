import tensorflow.keras as keras
from tensorflow.keras.layers import *
from tensorflow.keras.initializers import *
import tensorflow as tf

"""
ADD EXPERIENCE REPLAY (LEARNING FROM PAST MOVES), ACTIONS, AND HOOK IT UP TO WORKING 2048
ALSO GET SLOWLY DECREASING EPSILON AND GRAPH THE GAME SCORE OVER TIME
"""

class DQNAgent():
    def __init__(self, state_dim: tuple, action_dim):
        """
        :param tuple state_dim: a tuple with the (xdim, ydim) of the board
        :param int action_dim: an int with the possible actions, 4 in the case of 2048
        """
        self.state = state_dim
        self.action = action_dim
        self.construct_net()

    def construct_net(self):
        inp = Input(shape=self.state)
        hidden1 = Dense(
            25, activation="relu", kernel_initializer=he_normal()
        )(inp)
        hidden2 = Dense(
            25, activation="relu", kernel_initializer=he_normal()
        )(hidden1)
        hidden3 = Dense(
            25, activation="relu", kernel_initializer=he_normal()
        )(hidden2)
        q_values = Dense(
            self.action, kernel_initializer=Zeros(), activation="linear"
        )(hidden3)

        self.net = keras.Model(inputs=inp, outputs=[q_values])