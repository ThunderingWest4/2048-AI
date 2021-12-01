from pygame.constants import K_DOWN
from game import *
import pygame
from agent import *

if __name__ == "__main__":
    pygame.init() # initiating the module
    res = (600, 600) # setting the height, length of the window. easier to store in a variable for accessing later in program
    scrn = pygame.display.set_mode(res) # giving you a surface of said resolution, you need this to draw shapes onto
    font = pg.font.Font(pg.font.get_default_font(), 72)

    gameBoard = board(scrn, res, font)
    gameBoard.reset((4, 4)) # making sure it has default values

    running = True

    # gameloop
    # play through the ame, choose between greedy strategy and the net predicting
    while running:
        gameBoard.render()



        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    gameBoard.act(0)
                elif event.key == pygame.K_UP:
                    gameBoard.act(1)
                elif event.key == pygame.K_LEFT:
                    gameBoard.act(2)
                elif event.key == pygame.K_RIGHT:
                    gameBoard.act(3)
                elif event.key == pygame.K_q:
                    pygame.quit()
                    a = 3
                    a[0]
