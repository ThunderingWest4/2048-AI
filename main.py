from pygame.constants import K_DOWN
from game import *
import pygame
from agent import *
from collections import deque

pygame.init() # initiating the module
res = (600, 600) # setting the height, length of the window. easier to store in a variable for accessing later in program
scrn = pygame.display.set_mode(res) # giving you a surface of said resolution, you need this to draw shapes onto
font = pg.font.Font(pg.font.get_default_font(), 72)

gameBoard = board(scrn, res, font)
gameBoard.reset((4, 4)) # making sure it has default values

epsilon = 1
max_eps = 1
min_eps = 0.01
eps_decay = 0.01

player = DQNAgent((4, 4), 4, 30_000, epsilon, min_eps, max_eps, eps_decay)

episodes = 20_000
rewards = []
episode_len = []

for i in range(episodes):
    
    clock = pygame.time.Clock()
    FPS = 40

    # gameloop
    # play through the game, choose between greedy strategy and the net predicting
    state = gameBoard.reset((4, 4)) # making sure it has default values
    done = False
    total_loss = 0
    ep_len = 0
    total_reward = 0

    while not done:

        gameBoard.render()

        if random.random() <= player.eps:
            action = gameBoard.sample()
        else: 
            action = player.act(state)
        # debugging
        # action = player.act(state)

        next_state, reward, done = gameBoard.act(action)

        total_reward += reward
        ep_len += 1

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                # if event.key == pygame.K_DOWN:
                #     gameBoard.act(0)
                # elif event.key == pygame.K_UP:
                #     gameBoard.act(1)
                # elif event.key == pygame.K_LEFT:
                #     gameBoard.act(2)
                # elif event.key == pygame.K_RIGHT:
                #     gameBoard.act(3)
                # elif event.key == pygame.K_r:
                #     # quick board reset for testing purposes
                #     gameBoard.reset((4, 4))
                # elif event.key == pygame.K_q:
                #     pygame.quit()
                #     a = 3
                #     a[0]
                if event.key == pygame.K_q:
                    pygame.quit()
                    a = 3
                    a[0]
                    # hard exit
        state = next_state
        clock.tick(FPS)
    
    # means game is over if running this code
    player.updateEps(i)
    print(f"Completed episode {i} with total reward of {total_reward} with epsilon {player.eps}")
