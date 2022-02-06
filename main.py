from pygame.constants import K_DOWN
from game import *
import pygame
from agent import *
import matplotlib.pyplot as plt

"""
ISSUE: EACH ACTION GIVES IT A REWARD SO IT KEEPS PURSUING IMMEDIATE REWARDS RATHER THAN A LONG TERM WIN
SOLUTION: RNN? OR MAYBE WEIGHTING THE REWARDS BASED ON TIME TO ACHIEVE REWARD
"""

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

# player = CNNAgent((4, 4), 4, 30_000, epsilon, min_eps, max_eps, eps_decay)
player = DQNAgent((4,4), 4, 30_000, epsilon, min_eps, max_eps, eps_decay)
dqn = True

# collecting initial experiences
min_exp = 5_000
idx = 0
for i in range(min_exp):
    state = gameBoard.reset((4, 4))
    done = False
    ep_len = 0
    while not done:
        action = gameBoard.sample()

        # observation: [state, action, reward, next state, done]
        ep_len += 1
        state_n, reward, done = gameBoard.act(action)
        fix_s = player.convertState(state)
        fix_sn = player.convertState(state_n)
        # reward += 10*np.log2(ep_len) if reward != 0 else 0
        player.collect_exp([fix_s, action, reward, fix_sn, done])

        state = state_n
        idx += 1
        if idx >= min_exp:
            break

print("EXPERIENCE REPLAY INITIALIZED")

episodes = 500
rewards = []
episode_lens = []
losses = []
max_tiles = []

for i in range(episodes):
    
    # clock = pygame.time.Clock()
    # FPS = 40

    # gameloop
    # play through the game, choose between greedy strategy and the net predicting
    state = gameBoard.reset((4, 4)) # making sure it has default values
    done = False
    total_loss = 0
    ep_len = 0
    total_reward = 0
    steps_to_update = 0

    while not done:

        if random.random() <= player.eps:
            action = gameBoard.sample()
        else: 
            action = player.act(state)
        # debugging
        # action = player.act(state)

        next_state, reward, done = gameBoard.act(action)

        ep_len += 1
        # reward /= np.log(ep_len)
        # bot cheesed my gosh darn bad code
        # old reward algo: 
        # reward += 1.25*ep_len
        # except it could make a move that made no change on the board and still get rewarded because it 'survived'
        # so it kept making no change moves to cheese my bad code for free reward
        # idk if i should be proud, angry, confused, checking my code for more bugs, or all of the above
        # reward += 10*np.log2(ep_len) if reward != 0 else 0
        total_reward += reward
        steps_to_update += 1
        state = next_state

        fix_s = player.convertState(state)
        fix_sn = player.convertState(state_n)
        player.collect_exp([fix_s, action, reward, fix_sn, done])

        if steps_to_update % 4 == 0 or done:
            temp_loss = player.train(batch_size=1024)
            losses.append(temp_loss)
        
        # render every fourth game to help speed up bc no need for rendering
        # if i%1==0:
        gameBoard.render()

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                # manual controls for 2048
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

        # clock.tick(FPS)

    # means game is over if running this code
    if dqn:
        # added if-else to easlily switch btwn CNN/DQN w/o too much fiddling
        if steps_to_update >= 175:
            print("copying over weights")
            player.copy_weights()
            steps_to_update = 0
        
    player.updateEps(i)
    rewards.append(total_reward)
    episode_lens.append(ep_len)
    max_tiles.append(gameBoard.maxtile)
    print(f"Completed episode {i} with total reward of {total_reward} with epsilon {player.eps} amd highest tile {max_tiles[-1]}")

plt.plot(rewards)
plt.plot(episode_lens)
plt.plot(max_tiles)

plt.show()