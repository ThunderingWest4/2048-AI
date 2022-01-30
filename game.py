from grpc import stream_stream_rpc_method_handler
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
        self.streak = 0
        self.maxtile = 0

    def reset(self, dims: tuple):
        self.dimX = dims[0]
        self.dimY = dims[1]

        self.grid = np.array([[void() for i in range(self.dimX)] for i in range(self.dimY)])
        self.score = 0
        self.grid[random.randint(0, 3)][random.randint(0, 3)] = cell()

        self.done = False
        self.streak = 0
        self.maxtile = 0

        return self.grid # initial state

    def sample(self):
        # generate a random action
        return np.random.randint(0, 4)

    def act(self, move: int):
        """
        :param int move: an int in range [0, 3] representing the move where 0=up, 1=down, 2=left, 3=right
        """
        # action is either 0, 1, 2, 3 where
        # 0=up, 1=down, 2=left, 3=right
        game = []

        # jank getting the net reward but idk
        # taking score at beginning of round, doing the stuff, then finding the difference
        # for net reward
        scoreInit = self.score


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
        # print(np.size(game), np.size(self.grid), move)
        equalMats = self.isEqual(self.grid, game)
        # print(a)
        if not equalMats:
            #if move changed something
            self.grid = game
            self.spawnNewTile()

        # self.render()

        """
        more bonuses to incentivize program to git gud: 
        - streaks, (1+(0.1*x))*score if x>=1 where 'x' is the number of consecutive moves made that resulted in tiles being combined
        - - what if it was something like incrementing multiplier and for every move it doesnt score, it's decremented by 0.1 to a min of 1 to have it look beyond a single turn?
        - - combo for more tiles per turn bonus?
        - new high score, (1.5*new tile score) if it gets a new high tile (i.e. hits 8 for the first time, 16, etc.) 
        - some sort of addl time based bonus? maybe smth like (below)
        - - reward_step = (net score increase with chain/combo/new tile bonuses) + some regulizer to balance the multiplier * e^(game_len)
        - - issue is balancing the regulizer to allow score to incr and get boosted from longer game len w/o overshadowing the initial net score and making the net focus on surviving instead of higher scoring
        """

        compl = self.isComplete()
        self.done = False
        bonus = self.score - scoreInit
        if bonus > 0:
            self.streak += 1 # means that it merged at least one tile
            mult = 1+(0.2*self.streak)
            bonus *= mult # bonus = bonus*mult
        else:
            self.streak = 0 # reset sterak if broken

        if compl == 2048:
            # computer won
            bonus += 2048 # big bonus
            self.done = True
        elif compl == -1:
            # you lost
            self.done = True
            bonus -= 2048
        else:
            # game not over
            pass
        
        self.score += bonus

        return (self.grid, bonus, self.done)
                
    def isEqual(self, mat1, mat2):
        # updated is mat2, current is mat1, checking if they're equal/any change
        if(np.size(mat1) != np.size(mat2)):
            self.visMat(mat1)
            self.visMat(mat2)
            raise KeyError("bad size " + str(mat1) + " " + str(mat2))

        equal = True
        for i in range(self.dimX):
            for j in range(self.dimY):
                if mat2[i][j].val > self.maxtile: 
                    self.maxtile = mat2[i][j].val

                equal = equal and (mat1[i][j].val == mat2[i][j].val)
        
        return equal

    def visMat(self, mat):
        s = ""
        for i, x in enumerate(mat):
            s2 = ""
            for j, e in enumerate(x):
                s2 += str(e.val) + ","
            s+=s2+"\n"
        print(s)


    def isComplete(self):
        # checks if game over
        s = 0
        for i in range(4):
            for j in range(4):
                if(self.grid[i][j].val == 2048):
                    has2048 = True
                    return 2048
                for k in [j+1, j-1]:
                    if k >= 0 and k <= 3:
                        s += ((self.grid[i][j].val == self.grid[i][k].val) or (self.grid[i][k].val == 0))

                for k in [i+1, i-1]:
                    if k >= 0 and k <= 3:
                        s += (self.grid[i][j].val == self.grid[k][j].val)
        
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

        pg.display.set_caption(f"Score: {self.score} | Streak Mult: {1+(0.2*self.streak)}")

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


