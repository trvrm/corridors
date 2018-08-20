# coding: utf-8

import numpy as np
import attr
import copy
import functools
import datetime

from . import balanced_ternary

from attr.validators import instance_of

from . import movement
from .movement import UP,DOWN, LEFT,RIGHT, canEscape
from .movement import EMPTY,HORIZONTAL,VERTICAL

    
def defaultDrawnGrid(N):
    characters=np.full((N*2,N*4)," ")
    for j in range(0,N*2,2):
        for i in range(0,N*4,4):
            if j>0:
                characters[j-1,i]   = '─'
                characters[j-1,i+1] = '─'
                characters[j-1,i+2] = '─'
                if i<(N*4-4):
                    characters[j-1,i+3]='┼'
            if i>0:
                characters[j,i-1]="│"
    return characters

@attr.s
class Piece:
    color    = attr.ib()
    location = attr.ib(validator=instance_of(tuple))
    walls    = attr.ib()
    N        = attr.ib()

    def hasWon(self):
        j=self.location[0]
        return (
            ((self.color=='red') and (j==0))
            or
            ((self.color=='blue') and (j==self.N-1))
        )
    def __json__(self):
        return {
            "color":self.color,
            "location":self.location,
            "walls":self.walls,
            
            
        }

def locationFromDirection(location,direction):
    
    j,i=location
    if 'up'   == direction:   return j-1,i
    if 'down' == direction:   return j+1,i
    if 'left' == direction:   return j,  i-1
    if 'right'== direction:   return j,  i+1
    
def hopTarget(location,d1,d2):
    location = locationFromDirection(location,d1)
    location = locationFromDirection(location,d2)
    return location
    
class BrokenRule(Exception):
    pass
    
class GameOver(Exception):
    pass


def ruleCheck(condition,message):
    if not condition:
        raise BrokenRule(message)
    
def perpendicular(d1,d2):
    if d1 in ['up','down']:
        return d2 in ['left','right']
    else:
        return d2 in ['up','down']
        

HOP_COMMANDS = [
    ['hop', 'up', 'up'],
    ['hop', 'up', 'left'],
    ['hop', 'up', 'right'],
    ['hop', 'down', 'down'],
    ['hop', 'down', 'left'],
    ['hop', 'down', 'right'],
    ['hop', 'left', 'up'],
    ['hop', 'left', 'down'],
    ['hop', 'left', 'left'],
    ['hop', 'right', 'up'],
    ['hop', 'right', 'down'],
    ['hop', 'right', 'right']
]

MOVE_COMMANDS=[
    ['move','up'],
    ['move','down'],
    ['move','left'],
    ['move','right'],
]


@functools.lru_cache()
def wallCommands(boardSize):
    M = boardSize-1
    return [
        [cmd, (j, i)]
        for cmd in ['hwall','vwall']
        for j in range(M)
        for i in range(M)
    ]

@functools.lru_cache()
def boardCommands(boardSize):
    return MOVE_COMMANDS+HOP_COMMANDS+wallCommands(boardSize)
    
    
class Board:
    def __init__(self):
        '''
            The wall grid is the grid of intersections of the wall slots, so is 8x8.
            The movement grid is the grid of squares, so 9x9
            (Assuming standard size board)
        '''
        self.N = self.boardSize = 9
        self.wallsPerPiece      = 10
        self.reset()
        
        # set this to false e.g. in tree searches when we know 
        # we're only applying valid commands
        self.do_checks=True
        
    def __hash__(self):
        walls = balanced_ternary.decode(self.walls.flatten())
        return hash((self.red, self.blue, self.turn, walls))
        
    def reset(self):
        N               = self.N
        M               = N-1
        self.walls      = np.full((M,M),EMPTY, dtype=np.int32)
        i               = int(N/2)
        self.red        = Piece('red', location=(M,i), N=N, walls=self.wallsPerPiece)
        self.blue       = Piece('blue',location=(0,i), N=N, walls=self.wallsPerPiece)

        self.turn       ='red'
        #self.history    = []
        
    def __json__(self):
        return{
    
            "red":self.red,
            "blue":self.blue,
        
            "walls":[
                [int(cell) for cell in row]
                for row in self.walls
            ],
            # "history":self.history,
            "turn":self.turn,
            "settings":{
                "N":self.N,
                "walls_per_piece":self.wallsPerPiece
            },
            
        }
    
    def __eq__(self, other):
        return all([
            (self.N==other.N),
            (self.walls==other.walls).all(),
            (self.red==other.red),
            (self.blue==other.blue),
            (self.turn==other.turn)
        ])
    
    
    def __deepcopy__(self,memo):
        
        board=Board()
        board.walls=self.walls.copy()
        board.red.location=self.red.location
        board.blue.location=self.blue.location
        board.red.walls=self.red.walls
        board.blue.walls=self.blue.walls
        board.turn=self.turn
        return board

    def gameOver(self):
        return self.red.hasWon() or self.blue.hasWon()
    
    def winner(self):
        if self.red.hasWon():return 'red'
        if self.blue.hasWon():return 'blue'
    
    
        
    def info(self):
        
        winBanner=""
        if self.red.hasWon():
            winBanner="RED HAS WON"
        if self.blue.hasWon():
            winBanner="BLUE HAS WON"
        return """
            {} player's turn
            Red walls:  {}
            Blue walls: {}
            {}
        """.format(self.turn.capitalize(),self.red.walls,self.blue.walls,winBanner)        
    
    def legalHop(self, location, d1, d2):
        
        l1 = locationFromDirection(location,d1)
        
        # square described by l1 MUST contain a piece.
        if (self.red.location!=l1) and (self.blue.location!=l1):
            return False
            
        # must be able to move to l1
        if not self.legalMove(location,d1,checkPieces=False):
            return False
        
        # if we CAN continue in the same direction, we MUST
        if self.legalMove(l1,d1):
            return d2==d1
        else:
            # else d2 must be perpendicular to d1 AND
            # d1->d2 must be legal    
            return perpendicular(d1,d2) and self.legalMove(l1,d2)
        
        
    def legalMove(self,location,direction, checkPieces=True):
        
        j,i=location
        N=self.N
        M=N-1
        
        assert direction in ('up','down','left','right')
        
        # check edges first
        if (j==0)        and (direction=='up'):    return False
        if (j>=M)        and (direction=='down'):  return False
        if (i==0)        and (direction=='left'):  return False
        if (i>=M)        and (direction=='right'): return False
        
        # check piece location
        
        # we DON'T want to to do this check when testing escapability!
        if checkPieces:
            target = locationFromDirection(location, direction)
            if(self.red.location==target or self.blue.location==target):
                return False
        
        # Check Walls
        if 'up'==direction:
            if i>0:
                if self.walls[(j-1,i-1)]==HORIZONTAL: return False
            if i<M:
                if self.walls[(j-1,i  )]==HORIZONTAL: return False

        if 'left'==direction:    
            if j>0:
                if self.walls[(j-1,i-1)]==VERTICAL: return False
            if j<M:
                if self.walls[(j  ,i-1)]==VERTICAL: return False

        if 'right'==direction:
            if j>0:
                if self.walls[(j-1,i   )]==VERTICAL: return False
            if j<M:
                if self.walls[(j  ,i  )]==VERTICAL: return False

        if 'down'==direction:
            if i>0:
                if self.walls[(j  ,i-1)]==HORIZONTAL: return False
            if i<M:
                if self.walls[(j  ,i  )]==HORIZONTAL: return False

        return True 
    
    
    def canEscape(self,piece):
        return canEscape(self,piece)
        
      
      
        
    def piecesCanEscape(self):
        return (
            self.canEscape(self.red)
            and
            self.canEscape(self.blue)
        )
    
    def legalWall(self,location,orientation):
        j,i=location
        return movement.legalWall(self.walls,j,i,orientation)
        
    
    def escapableWall(self,location,orientation):
        'put it on, test, take it off!'
        assert orientation in (HORIZONTAL,VERTICAL), orientation
        j,i=location
        M=self.N-1
        walls=self.walls
        assert 0<=j<M
        assert 0<=i<M
        
        walls[location] = orientation
        escapable       = self.piecesCanEscape()
        walls[location] = 0
        return            escapable
    
    def _addWall(self,location, orientation):
        assert len(location)==2
        location=tuple(location)  # in case it's a list
        
        assert not self.gameOver(), "Game over, dude!"
        assert orientation in (HORIZONTAL,VERTICAL)
        
        color   = self.turn
        piece   = getattr(self,color)
        
        if self.do_checks:
            ruleCheck(piece.walls>0, "No walls left")
            ruleCheck(self.legalWall(location,orientation), "illegal wall at {}: {}".format(location,orientation))
            ruleCheck(self.escapableWall(location,orientation),"trapping wall at {}: {}".format(location,orientation))
        
        self.walls[location]=orientation
        piece.walls-=1
        
    def _hwall(self,location):
        self._addWall(location,HORIZONTAL)
        
    def _vwall(self,location):
        self._addWall(location,VERTICAL)
        
    def _hop(self,d1,d2):
        assert not self.gameOver(), "Game over, dude!"
        color=self.turn
        
        assert d1 in ('up','down','left','right')
        assert d2 in ('up','down','left','right')
        
        piece = getattr(self,color)
        
        if self.do_checks:
            ruleCheck(
                self.legalHop(piece.location,d1,d2),
                "illegal hop for {}: {} {}".format(color,d1,d2)
            )
        # if it's legal...
        piece.location = locationFromDirection(piece.location,d1)
        piece.location = locationFromDirection(piece.location,d2)
        
    
    
    
    def _move(self, direction):
        assert not self.gameOver(), "Game over, dude!"
        assert direction in ('up','down','left','right')
        
        color=self.turn
        piece = getattr(self,color)

        if self.do_checks:
            ruleCheck(
                self.legalMove(piece.location,direction),
                "illegal move for {}: {}".format(color,direction)
            )
        
        piece.location = locationFromDirection(piece.location,direction)
        
    def _endTurn(self):
        self.turn = 'red' if self.turn=='blue' else 'blue'
    
    
    def currentPiece(self):
        return getattr(self,self.turn)
    
    def legalCommand(self,command):
        if self.gameOver():return False
        action  = command[0]
        piece   = self.currentPiece()
        
        if 'hop'==action:
            return self.legalHop(piece.location, *command[1:])
        if 'move'==action:
            return self.legalMove(piece.location, *command[1:])
        if action in ('vwall','hwall'):
            orientation = HORIZONTAL if action=='hwall' else VERTICAL
            
            # messy, we should fix
            location=command[1]
            assert len(location)==2
            location=tuple(location)  # in case it's a list
            return (
                piece.walls>0
                and self.legalWall(location,orientation) 
                and self.escapableWall(location,orientation)
            )
        return False
    
    def __call__(self,*command):
        action=command[0]
        
        if self.do_checks:
            if self.gameOver(): BrokenRule( "Game over, dude!")
            assert action in ('move','hwall','vwall','hop'),action
            if not self.legalCommand(command):
                raise BrokenRule("Illegal command: {}".format(command))
                
        fn=getattr(self,'_'+action)
        fn(*command[1:])
        self._endTurn()
        
        
    def __repr__(self):
        
        characters=defaultDrawnGrid(self.N)
        
        j,i=self.red.location
        characters[(j*2),(i*4)+1]='R'
        j,i=self.blue.location
        characters[(j*2),(i*4)+1]='B'
        
        # now draw on the walls
        for j,rows in enumerate(self.walls):
            for i,wall in enumerate(rows):
                if wall==HORIZONTAL:
                    for ii in range(7):
                        characters[(j*2)+1,(i*4)+ii]='═'  
                if wall==VERTICAL:
                    for jj in range(3):
                        characters[(j*2)+jj,(i*4)+3]='║'  
            
         
        return "\n".join(
            "".join(line)
            for line in characters
        )+self.info()+'-'*20+'\n\n'

    def allLegalCommands(self):
        '''
            I suspect if _this_ was a generator, 
            then we could get some awesome early-termination speedups in a 
            pruning tree search.  I.e. if we aborted early, we wouldn't have to 
            even check the legality of later commands 
            
            This should be set/cached every time we make a move.
        '''
        return (
            command
            for command in boardCommands(self.N)
            if self.legalCommand(command)
        )


    
    
    
def encode(board):
    assert board.N<10
    walls =  balanced_ternary.decode(board.walls.flatten())
    extra = "{}.{}.{}.{}.{}.{}.{}.{}.{}.".format(
        board.N,
        board.wallsPerPiece,
        board.red.location[0],
        board.red.location[1],
        board.red.walls,
        board.blue.location[0],
        board.blue.location[1],
        board.blue.walls,
        int(board.turn=='red')

    )
    return  extra + str(walls)

def decode(s):
    N, wallsPerPiece, rl0, rl1, rwalls, bl0,bl1, bwalls, turn, walls = [int(el) for el in s.split('.')]
    
    walls = balanced_ternary.encode(walls)
    while(len(walls)<(N-1)**2):
        walls.insert(0,0)

    board=Board(N,wallsPerPiece)
    board.walls = np.array(walls).astype('int32').reshape(N-1,N-1)
    board.red.location=rl0,rl1
    board.red.walls=rwalls
    board.blue.location=bl0,bl1
    board.blue.walls=bwalls
    board.turn = 'red' if turn else 'blue'
    return board    