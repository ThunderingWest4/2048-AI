import pygame as pg
from colors import *

class cell():
    def __init__(self):
        self.val = 2 # default start
        self.merged = False

class void():
    def __init__(self):
        self.val = 0 # empty space
        self.merged = False

class board():

    def __init__(self, screen, res, font):
        self.scrn = screen
        self.res = res
        self.font = font

    def reset(self, dims: tuple):
        self.dimX = dims[0]
        self.dimY = dims[1]

        self.grid = [[void() for i in range(self.dimX)] for i in range(self.dimY)]
        self.score = 0

    def act(self, move: int):
        # action is either 0, 1, 2, 3 where
        # 0=up, 1=down, 2=left, 3=right

        if(move == 0):
            pass
        
        

    def render(self):

        xIncr = self.res[0] // self.dimX
        yIncr = self.res[1] // self.dimY

        for i, row in enumerate(self.grid):
            for j, cell in enumerate(row):
                
                col = cellCol[cell.val] if cell.val in cellCol.keys() else backupCellCol
                textCol = (0, 0, 0) if cell.val in [2, 4] else (238, 228, 213)

                pg.draw.rect(self.scrn, col, pg.Rect(i*xIncr+5, j*yIncr+5, xIncr-10, yIncr-10))

                text_surface = self.font.render(str(cell.val), True, textCol)
                self.scrn.blit(text_surface, dest=((i*xIncr+55), (j*yIncr+40)))


        pg.display.flip()



