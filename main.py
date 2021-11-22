from game import *
import pygame

pygame.init() # initiating the module
res = (600, 600) # setting the height, length of the window. easier to store in a variable for accessing later in program
scrn = pygame.display.set_mode(res) # giving you a surface of said resolution, you need this to draw shapes onto
font = pg.font.Font(pg.font.get_default_font(), 72)

gameBoard = board(scrn, res, font)
gameBoard.reset((4, 4)) # making sure it has default values

running = True

# gameloop
while running:
    gameBoard.render()

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                pygame.quit()
