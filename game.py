from numpy.core.defchararray import translate
from numpy.core.fromnumeric import transpose
import pygame as pg
import numpy as np
from colors import *
import random

class cell():
    def __init__(self):
        self.val = 2 # default start
        self.merged = False
        self.isEmpty = False

class void():
    def __init__(self):
        self.val = 0 # empty space
        self.merged = False
        self.isEmpty = True

class board():

    def __init__(self, screen, res, font):
        self.scrn = screen
        self.res = res
        self.font = font

    def reset(self, dims: tuple):
        self.dimX = dims[0]
        self.dimY = dims[1]

        self.grid = np.array([[void() for i in range(self.dimX)] for i in range(self.dimY)])
        self.score = 0
        self.grid[random.randint(0, 3)][random.randint(0, 3)] = cell()

    def act(self, move: int):
        """
        :param int move: an int in range [0, 3] representing the move where 0=up, 1=down, 2=left, 3=right
        """
        # action is either 0, 1, 2, 3 where
        # 0=up, 1=down, 2=left, 3=right
        game = []

        # method functions are weird, idk why they're like this but don't question it
        # i blame the person who i borrowed the code from

        if(move == 0):
            game, _ = self.right(self.grid)
        elif(move == 1):
            game, _ = self.left(self.grid)
        elif(move == 2):
            game, _ = self.up(self.grid)
        elif(move == 3):
            game, _ = self.down(self.grid)
        
        # print(game, self.grid)
        # print(np.size(game), np.size(self.grid))
        equalMats = self.isEqual(self.grid, game)
        # print(a)
        if not equalMats:
            #if move changed something
            self.grid = game
            self.spawnNewTile()

        self.render()

        compl = self.isComplete()
        done = False
        if compl == 2048:
            # computer won
            self.score += 2048 # big bonus
            done = True
        elif compl == 1:
            # you lost
            done = True
        else:
            # game not over
            pass


        
                
    def isEqual(self, mat1, mat2):
        if(np.size(mat1) != np.size(mat2)):
            raise KeyError("bad size")

        equal = True
        for i in range(self.dimX):
            for j in range(self.dimY):
                equal = equal and (mat1[i][j].val == mat2[i][j].val)
        
        return equal

    def isComplete(self):
        has2048 = False
        s = 0
        for i in range(4):
            for j in range(4):
                if(self.grid[i][j].val == 2048):
                    has2048 = True
                    return 2048
                for k in [j+1, j-1]:
                    if k >= 0 and k <= 3:
                        s += self.grid[i][j].val == self.grid[i][k].val
        
        # s>0 means that at least one is true therefore at least one possible move
        if s>0:
            return 1
        else:
            return -1

        
    def spawnNewTile(self):
        emptyTiles = []
        for i in range(self.dimX):
            for j in range(self.dimY):
                if self.grid[i][j].isEmpty:
                    emptyTiles.append((i, j))
        if emptyTiles != []:
            coords = random.choice(emptyTiles)
            # NOTE TO SELF: ADD SPAWNING IN 4s LATER ON FOR MORE REALISTIC GAMEPLAY

            self.grid[coords[0]][coords[1]] = cell()



    def render(self):

        pg.display.set_caption(f"Score: {self.score}")

        self.scrn.fill((0, 0, 0)) # clear screen before rendering

        xIncr = self.res[0] // self.dimX
        yIncr = self.res[1] // self.dimY

        for i, row in enumerate(self.grid):
            for j, cell in enumerate(row):
                
                col = cellCol[cell.val] if cell.val in cellCol.keys() else backupCellCol
                textCol = (0, 0, 0) if cell.val in [2, 4] else (238, 228, 213)

                pg.draw.rect(self.scrn, col, pg.Rect(i*xIncr+5, j*yIncr+5, xIncr-10, yIncr-10))

                text_surface = self.font.render(str(cell.val), True, textCol)

                # dest
                l = len(str(cell.val))

                d = ()
                if l <= 1:
                    d = ((i*xIncr+55), (j*yIncr+40))
                elif l == 2:
                    d = ((i*xIncr+40), (j*yIncr+40))
                elif l == 3:
                    d = ((i*xIncr+15), (j*yIncr+40))
                elif l == 4:
                    d = ((i*xIncr), (j*yIncr+40))

                self.scrn.blit(text_surface, dest=d)


        pg.display.flip()

    # MOVE CODE IS *EXTREMELY* LONG AND SPAGHETTI AND I COULD PROBABLY CONDENSE IT
    # BUT INSTEAD I'M JUST GONNA HIDE IT DOWN HERE
    # ENJOY

    # 2048 base logic code adapted from https://github.com/yangshun/2048-python/blob/master/

    def reverse(self, mat):
        return np.flip(mat)

    def transpose(self, mat):
        return np.transpose(mat)

    def cover_up(self, mat):
        new = []
        for j in range(self.dimX):
            partial_new = []
            for i in range(self.dimY):
                partial_new.append(void())
            new.append(partial_new)
        done = False
        for i in range(self.dimX):
            count = 0
            for j in range(self.dimY):
                if mat[i][j].val != 0:
                    new[i][count] = mat[i][j]
                    if j != count:
                        done = True
                    count += 1
        return new, done

    def merge(self, mat, done):
        for i in range(self.dimX):
            for j in range(self.dimY-1):
                if mat[i][j].val == mat[i][j+1].val and mat[i][j].val != 0:
                    mat[i][j].val *= 2
                    # incr score
                    self.score += mat[i][j].val
                    mat[i][j+1] = void()
                    done = True
        return mat, done

    def up(self, game):
        # print("up")
        # return matrix after shifting up
        game = transpose(game)
        game, done = self.cover_up(game)
        game, done = self.merge(game, done)
        game = self.cover_up(game)[0]
        game = transpose(game)
        return game, done

    def down(self, game):
        # print("down")
        # return matrix after shifting down
        game = self.reverse(transpose(game))
        game, done = self.cover_up(game)
        game, done = self.merge(game, done)
        game = self.cover_up(game)[0]
        game = transpose(self.reverse(game))
        return game, done

    def left(self, game):
        # print("left")
        # return matrix after shifting left
        game, done = self.cover_up(game)
        game, done = self.merge(game, done)
        game = self.cover_up(game)[0]
        return game, done

    def right(self, game):
        # print("right")
        # return matrix after shifting right
        game = self.reverse(game)
        game, done = self.cover_up(game)
        game, done = self.merge(game, done)
        game = self.cover_up(game)[0]
        game = self.reverse(game)
        return game, done


