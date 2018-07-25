import numpy as np
import functools
import random
import datetime
import logging
import copy
import math
from .utilities import timed
from .movement import stepsToEscape, canMove, UP,DOWN

now=datetime.datetime.now
INFINITY=float('inf')


def apply_command(board,command):
    '''
        assumes command is legal
    '''
    clone = copy.deepcopy(board)
    clone.do_checks=False
    clone(*command)
    
    return clone
    
    
class BaseBot:
    def __str__(self):
        return self.__class__.__name__
    def __init__(self,name=None):
        self.name=name
    def __json__(self):
        return {
            "type":str(type(self)),
            "name":getattr(self,'name','unnamed')
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
        positions     = [apply_command(board,command) for command in commands]
        scores        = [self.evaluate(position) for position in positions]
        
        commandScores = list(zip(commands,scores))
        commandScores.sort(key = lambda p: p[1])
        
        if board.turn=='red':
            best=commandScores[-1]
        else:
            best=commandScores[0]

        command,score=best
        return command
    
   
class RandomBot(BaseBot):
    def __call__(self, board):
        return random.choice(list(board.allLegalCommands()))
        
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
            

class StepsBot(BaseBot):
    '''
        This is staggeringly stupid, treats some losing positions as equal to non-losing ones.
    '''
    def evaluate(self,board):
        '+ve = good red position, i.e. short distance for red, long for blue'
        
        if board.red.hasWon(): return INFINITY
        if board.blue.hasWon():return -INFINITY
        
        redDistance  = stepsToEscape(board,board.red)
        blueDistance = stepsToEscape(board,board.blue)
        return blueDistance-redDistance
    
    

class StepsBot2(BaseBot):
    def evaluate(self,board):
        '+ve = good red position, i.e. short distance for red, long for blue'
        
        if board.red.hasWon(): return INFINITY
        if board.blue.hasWon():return -INFINITY
        
        r  = 0.5+  stepsToEscape(board,board.red)
        b  = 0.5+  stepsToEscape(board,board.blue)
        return b/r -1 if r<b else 1 -(r/b)
    
    
    
class StepsBot3(BaseBot):
    def evaluate(self,board):
        
        WEIGHT=0.1
        N=board.N
        
        def _evaluate(red_distance,blue_distance,red_to_play):
            if red_to_play:
                blue_distance+=1
            else:
                red_distance+=1
            
            blue_distance=math.log(1+blue_distance)
            red_distance=math.log(1+red_distance)
            return blue_distance-red_distance

        
        wallScore     = math.log(1+board.red.walls)-math.log(1+board.blue.walls)
        return _evaluate(
            stepsToEscape(board,board.red),
            stepsToEscape(board,board.blue),
            board.turn=='red'
        )+WEIGHT*wallScore
    


class DumbBot(BaseBot):
    def evaluate(self,board):
        if board.red.hasWon(): return INFINITY
        if board.blue.hasWon():return -INFINITY
        
        red_distance=(board.red.location[0]-0)
        blue_distance=(8-board.blue.location[0])
        
        return blue_distance-red_distance
    
    
        

class AlphaBetaBot(BaseBot):
    
    MAX_AB_CALLS=10000
    def __init__(self,evalBot,maxDepth=1):
        self.maxDepth=maxDepth
        self.evalBot = evalBot
        
    def __str__(self):
    
        eval_bot_name=str(self.evalBot)
        return f"AlphaBetaBot<{eval_bot_name}>"
        
    def alphabeta(self, board,depth, α, β):
        
        if depth==0:
            return self.evalBot.evaluate (board), None

        if board.gameOver():
            return self.evalBot.evaluate (board), None

        self.ab_calls+=1
        
        commands      = list(board.allLegalCommands())
        children      = [apply_command(board,command) for command in commands]
        
        if board.turn=='red':
            v= -INFINITY
            best_command = commands[0]
            for command in commands:
                child = apply_command(board,command)
                score,_ = self.alphabeta(child,depth-1,α,β)
                
                if score > v:
                    v=score
                    best_command=command
                #v = max(v, score)  # which command gives us this?
                α = max(α,v)
                if β<=α: break
                
                if self.ab_calls>= AlphaBetaBot.MAX_AB_CALLS:
                    logging.warning('max ab calls')
                    break
                
            return v, best_command
        else: # blue
            v= + INFINITY
            best_command = commands[0]
            for command in commands:
                child = apply_command(board,command)
                score,_ = self.alphabeta (child,depth-1,α,β)
                
                if score < v:
                    v=score
                    best_command = command
                #v = min(v, score)
                β = min(β,v)
                if β<=α: break
                if self.ab_calls>= AlphaBetaBot.MAX_AB_CALLS:
                    logging.warning('max ab calls')
                    break
            return v, best_command

    
    def evaluate(self,board):
        assert 0

    def __call__(self,board):
        
        self.ab_calls=0
        maxDepth = 3
        
        logging.info(f"{self}.__call__(), maxDepth:{maxDepth}")
        with timed():
            score, command = self.alphabeta(board,maxDepth,-INFINITY,INFINITY)
        
        logging.info(f"score:{score}, command: {command}, ab_calls: {self.ab_calls}")
        
        
        return command
        
        
        
