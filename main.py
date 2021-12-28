from pygame.constants import K_DOWN
from game import *
import pygame
from agent import *
import matplotlib.pyplot as plt

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

# collecting initial experiences
min_exp = 2_000
idx = 0
for i in range(min_exp):
    state = gameBoard.reset((4, 4))
    done = False
    while not done:
        action = gameBoard.sample()

        # observation: [state, action, reward, next state, done]

        state_n, reward, done = gameBoard.act(action)
        fix_s = player.convertState(state)
        fix_sn = player.convertState(state_n)
        player.collect_exp([fix_s, action, reward, fix_sn, done])

        state = state_n
        idx += 1
        if idx >= min_exp:
            break

print("EXPERIENCE REPLAY INITIALIZED")

episodes = 20_000
rewards = []
episode_lens = []
losses = []

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

        total_reward += reward
        ep_len += 1
        steps_to_update += 1
        state = next_state

        fix_s = player.convertState(state)
        fix_sn = player.convertState(state_n)
        player.collect_exp([fix_s, action, reward, fix_sn, done])

        if steps_to_update % 4 == 0 or done:
            temp_loss = player.train(batch_size=256)
            losses.append(temp_loss)
        
        # render every fourth game to help speed up bc no need for rendering
        if i%4==0:
            gameBoard.render()

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

        # clock.tick(FPS)

    # means game is over if running this code
    if steps_to_update >= 175:
        print("copying over weights")
        player.copy_weights()
        steps_to_update = 0
    
    player.updateEps(i)
    rewards.append(total_reward)
    episode_lens.append(ep_len)
    print(f"Completed episode {i} with total reward of {total_reward} with epsilon {player.eps}")

plt.plot(rewards)
plt.plot(episode_lens)

plt.show()