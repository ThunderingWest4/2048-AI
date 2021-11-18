class board():
    def reset(self, dims: tuple):
        self.dimX = dims[0]
        self.dimY = dims[1]

        self.grid = [[0 for i in range(self.dimX)] for i in range(self.dimY)]
        self.score = 0

    def act(self, move: int):
        # action is either 0, 1, 2, 3 where
        # 0=up, 1=down, 2=left, 3=right

        if(move == 0):
            pass
        
        

    def render(self):
        pass
