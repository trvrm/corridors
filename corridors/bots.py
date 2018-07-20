# -*- coding: utf-8 -*-
import numpy as np
import functools
import random
import datetime
import logging

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
        positions     = [applyCommand(board,command) for command in commands]
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


class AlphaBetaBot(BaseBot):
    '''
        Way better!
    '''
    def __init__(self,evalBot,maxDepth=1):
        self.maxDepth=maxDepth
        self.evalBot = evalBot
        
    def alphabeta(self, board,depth, α, β):
        
        if depth==0:
            return self.evalBot.evaluate (board)

        if board.gameOver():
            return self.evalBot.evaluate (board)

        commands      = list(board.allLegalCommands())
        children      = [board.apply(command) for command in commands]
        
        if board.turn=='red':
            v= -INFINITY
            for command in commands:
                child = board.apply(command)
                score = self.alphabeta(child,depth-1,α,β)
                v = max(v, score)
                α = max(α,v)
                if β<=α: break
            return v
        else: # blue
            v= + INFINITY
            for command in commands:
                child = board.apply(command)
                score = self.alphabeta (child,depth-1,α,β)
                v = min(v, score)
                β = min(β,v)
                if β<=α: break
            return v

    
    def evaluate(self,board):
        #print('AB evaluate max depth = {}'.format(self.maxDepth))
        score = self.alphabeta(board, self.maxDepth,-INFINITY,INFINITY)
        return score
        
    '''    
    def __call__(self,board):
        
        commands      = list(board.allLegalCommands())
        children      = [applyCommand(board,command) for command in commands]
        
        
        return command'''