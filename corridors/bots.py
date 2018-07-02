import numpy as np
import functools
import random
#import pandas
import copy
#import game
import datetime


import numpy as np



from .movement import stepsToEscape

now=datetime.datetime.now
INFINITY=float('inf')


def applyCommand(board,command):
    return board.apply(command)
    
class BaseBot:
    def __str__(self):
        return self.__class__.__name__
    def __init__(self,name=None):
        self.name=name
    def __json__(self):
        return {
            "type":str(type(self)),
            "name":self.name
        }
    
    def evaluate(self,board):
        '''
        Must return a number
        +ve for good red positions
        -ve for good blue positions
        '''
        if board.red.hasWon(): return INFINITY
        if board.blue.hasWon():return -INFINITY
        return 0
    
    def __call__(self,board):
        '''
            Must return a legal command
        '''
        commands      = list(board.allLegalCommands())
        positions     = [applyCommand(board,command) for command in commands]
        scores        = [self.evaluate(position) for position in positions]
        
        commandScores = list(zip(commands,scores))
        commandScores.sort(key = lambda p: p[1])
        
        if board.turn=='red':
            return commandScores[-1][0]
            
        else:
            return commandScores[0][0]
            
        
        
        '''
        # maybe within a threshold?
        # this really needs to be optional behaviour
        
        threshold = 0.1
        if board.turn=='red':
            maxScore    = commandScores[-1][1]
            commands    = [c for c, s in commandScores if s+threshold > maxScore]
        else:
            minScore    = commandScores[0][1]
            commands    = [c for c, s in commandScores if s-threshold < minScore]
            
        return random.choice(commands)
        '''
   
class RandomBot(BaseBot):
    def __call__(self, board):
        return random.choice(list(board.allLegalCommands()))
        
        

class StepsBot(BaseBot):
    def evaluate(self,board):
        '+ve = good red position, i.e. short distance for red, long for blue'
        
        if board.red.hasWon(): return INFINITY
        if board.blue.hasWon():return -INFINITY
        
        redDistance  = stepsToEscape(board,board.red)
        blueDistance = stepsToEscape(board,board.blue)
        return blueDistance-redDistance
        
        
class StepsAndWallsBot(BaseBot):
    def __init__(self, weight,name=None):
        self.weight=weight
        self.name=name
        
    def evaluate(self,board):
        if board.red.hasWon(): return INFINITY
        if board.blue.hasWon():return -INFINITY
        
        redDistance  = stepsToEscape(board,board.red)
        blueDistance = stepsToEscape(board,board.blue)
        
        distanceScore = blueDistance-redDistance
        wallScore     = board.red.walls-board.blue.walls
        
        return distanceScore+self.weight*wallScore
        

class StepsBot2(BaseBot):
    def evaluate(self,board):
        '+ve = good red position, i.e. short distance for red, long for blue'
        
        if board.red.hasWon(): return INFINITY
        if board.blue.hasWon():return -INFINITY
        
        r  = 0.5+  stepsToEscape(board,board.red)
        b  = 0.5+  stepsToEscape(board,board.blue)
        return b/r -1 if r<b else 1 -(r/b)


class StepsAndWallsBot2(BaseBot):
    def __init__(self, weight,name=None):
        self.weight=weight
        self.name=name
        
    def evaluate(self,board):
        '+ve = good red position, i.e. short distance for red, long for blue'
        
        if board.red.hasWon(): return INFINITY
        if board.blue.hasWon():return -INFINITY
        
        r  = 0.5 +  stepsToEscape(board,board.red) - (self.weight*board.red.walls)
        b  = 0.5 +  stepsToEscape(board,board.blue) - (self.weight*board.blue.walls)
                
        return b/r -1 if r<b else 1 -(r/b)
        
class ModelBot(BaseBot):
    def __init__(self,model):
        self.model=model
        
    def evaluate(self,board):
        
        x = board.toArray()
        X = np.array([x])
        return self.model.predict(X)[0,0]
        
    def __call__(self,board):
        '''
            Must return a legal command
        '''
        commands      = board.allLegalCommands()
        X             = np.array([
            applyCommand(board,command).toArray() for command in commands
        ])
        

        scores        = self.model.predict(X)[:,0]
        commandScores = list(zip(commands,scores))
        
        maxScore      = max(scores)
        minScore      = min(scores)
        # pick randomly from equally scored commands - this could be tweaked I think
        # e.g. 'pick from top 10%', 'pick from top 2', 'pick from close to top'...
        
        if board.turn=='red':
            commands=[c for c, s in commandScores if s==maxScore]
        else:
            commands=[c for c, s in commandScores if s==minScore]
        return random.choice(commands)
        
        
class CombinedBot(BaseBot):
    def __init__(self, bot1, bot2, ratio):
        '''
            ratio is the likelihood of bot2 being used.
        '''
        self.bot1=bot1
        self.bot2=bot2
        self.ratio=ratio
        assert 0<=ratio<=1

    def __call__(self, board):
        if random.random() < self.ratio:
            return self.bot2(board)
        else:
            return self.bot1(board)
        

        
        
        
class MiniMax():
    '''
        Am I computing best score, best move, or both?
        Need to be careful here!
        
        What if 'depth' was adaptive?
    '''
    def __init__(self,evalBot):
        self.evalBot   = evalBot
        
    #@functools.lru_cache(1000000,typed=True)
    def __call__(self,board, depth):
        
        if board.red.hasWon(): return INFINITY
        if board.blue.hasWon():return -INFINITY
        
        if depth<=0:
            return self.evalBot.evaluate(board)
        else:
            
            commands     = board.allLegalCommands()
            
            children     = [applyCommand(board,command) for command in commands]
            scores       = [self(child,depth-1) for child in children]

            if board.turn=='red':
                return max(scores)
            else:
                return min(scores)


class MiniMaxBot(BaseBot):
    def __init__(self,evalBot,maxDepth):
        self.maxDepth=maxDepth
        self.minimax=MiniMax(evalBot)
    
    @functools.lru_cache(1000000,typed=True)
    def evaluate(self,board):
        return self.minimax(board,self.maxDepth)
        

class AlphaBetaBot(BaseBot):
    '''
        Way better!
    '''
    def __init__(self,evalBot,maxDepth=3):
        self.maxDepth=maxDepth
        self.evalBot = evalBot
        
    def alphabeta(self, board,depth, a,b):
        if depth==0:
            # terminal
            return self.evalBot.evaluate (board)

        if board.gameOver():
            return self.evalBot.evaluate (board)

        if board.turn=='red':
            v= -INFINITY
            for child in board.children():
                v= max(v, self.alphabeta(child,depth-1,a,b))
                a = max(a,v)
                if b<=a: break
            return v
        else:
            # turn is blue
            v= + INFINITY
            for child in board.children():
                v= min(v, self.alphabeta (child,depth-1,a,b))
                b =min(b,v)
                if b<=a: break
            return v

    
    def evaluate(self,board):
        return self.alphabeta(board, self.maxDepth,-INFINITY,INFINITY)
        
        
    
class AdaptiveDepthAlphaBetaBot(AlphaBetaBot):
    
    def __init__(self,evalBot):
        AlphaBetaBot.__init__(self,evalBot,0)
        
    def evaluate(self,board):
        assert 0, "don't call directl!"
    
    
    def complexity(self,board):
        cmds = list(board.allLegalCommands())
        cmds2= list(board.apply(cmds[0]).allLegalCommands())
        return len(cmds)+len(cmds2)
    
    def __call__(self,board):
        start=now()
        commands      = list(board.allLegalCommands())
        positions     = [applyCommand(board,command) for command in commands]
        
        
        maxDepth = 2 
        
        complexity = self.complexity(board)
        if complexity < 128:maxDepth=4
        if complexity < 80: maxDepth=7 
            
        scores        = [
            self.alphabeta(position, maxDepth,-INFINITY,INFINITY)
            for position in positions
        ]
        
        commandScores = list(zip(commands,scores))
        commandScores.sort(key = lambda p: p[1])
        
        duration=now()-start
        print("complexity:",complexity,"depth",maxDepth)
        if board.turn=='red':
            return commandScores[-1][0]
            
        else:
            return commandScores[0][0]
        
        
        
def playGame(redBot,blueBot,board):
    board.reset()
    while not board.gameOver():
        bot = blueBot if board.turn=='blue' else redBot
        command = bot(board)
        board(*command)
    return board.winner()
    
    
def playGames(bot1,bot2, board,rounds=10):
    '''
        Make it fair by playing both sides
    '''
    
    winners12 = [
        playGame(bot1,bot2,board)
        for i in range(int(rounds/2))
    ]
    
    winners21 = [
        playGame(bot2,bot1,board)
        for i in range(int(rounds/2))
    ]
    
    return {
        "bot1":winners12.count('red')+winners21.count('blue'),
        "bot2":winners21.count('red')+winners12.count('blue')
    }
    
    
    
    
# upgrade as we go!    
bestBot = StepsAndWallsBot(-0.14)    
    
def strength(bot,board):
    '''
        Compute the strength of a bot by playing it against successively stronger bots
        and finding where the win/loss ration drops below 1.
        
        Returns a number between 0 and 1
    '''
    def compare(bot,ratio):
        'Play 2 games against a bot at strength `i`'
        return playGames(
            bot,
            CombinedBot(
                RandomBot(),
                bestBot,  # Ideally this would be our best available bot
                ratio),
            board,
            rounds=2
        )['bot1']-1
    
    outcomes = pandas.DataFrame([
        {"ratio":i,"score":compare(bot,i)}
        for i in np.linspace(0,1,100)
    ])
    # took me a while...
    return ((outcomes.score+1)/2).sum()/100
    