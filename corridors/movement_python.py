'''
    Non cythonized version of movement functions
'''
import numpy as np
EMPTY      = 0
HORIZONTAL = 1
VERTICAL   = -1


UP    = 0
DOWN  = 1
LEFT  = 2
RIGHT = 3

def canMove(M,walls,  j,   i,   direction):
    if UP==direction:
        if j==0: return 0
        if i>0:
            if walls[(j-1,i-1)]==HORIZONTAL: return 0
        if i<M:
            if walls[(j-1,i  )]==HORIZONTAL: return 0
    
    if LEFT==direction:    
        if i==0: return 0
        if j>0:
            if walls[(j-1,i-1)]==VERTICAL: return 0
        if j<M:
            if walls[(j  ,i-1)]==VERTICAL: return 0
    
    if RIGHT==direction:
        if i>=M: return 0
        if j>0:
            if walls[(j-1,i   )]==VERTICAL: return 0
        if j<M:
            if walls[(j  ,i  )]==VERTICAL: return 0
    
    if DOWN==direction:
        if j>=M: return 0
        if i>0:
            if walls[(j  ,i-1)]==HORIZONTAL: return 0
        if i<M:
            if walls[(j  ,i  )]==HORIZONTAL: return 0
    
    return 1 



def stepsToEscape(board,piece):
    N = board.N
    M = N-1
    walls = board.walls
    squares = np.full((N,N),None)
  
    target_rank = 0 if piece.color=='red' else board.N-1
  
    location=(target_rank,0)
  
    neighbours=[(target_rank,i) for i in range(N)]
  
    steps=0
  
    for it in range(N**2):
        for (j,i) in neighbours:
            squares[j,i]=steps
            if (j,i)==piece.location:
                return squares[j,i]
      
        neighbours=[
            target
            for (jj,ii) in neighbours
            for direction,  target in [ (UP,(jj-1,ii)),(DOWN,(jj+1,ii)),(LEFT,(jj,ii-1)),(RIGHT,(jj,ii+1))]
            if canMove(M, walls, jj, ii, direction)
            if squares[target] is None
        ]
      
        neighbours=list(set(neighbours)) # remove dupes
        steps+=1
      
    assert 0, "no way out"
  


def canEscape(board,piece):
    walls = board.walls
    checked_squares = set()
    N = board.N
    M = N-1
    def inner(location, target_rank):
        j = location[0]
        i = location[1]
        if j==target_rank:              return True
        
        if location in checked_squares: return False
        checked_squares.add(location)
        
        for direction, target in ( (UP,(j-1,i)),(DOWN,(j+1,i)),(LEFT,(j,i-1)),(RIGHT,(j,i+1))):
            if target not in checked_squares:
                if canMove(M, walls,j,i,direction):
                    if inner(target,target_rank):
                        return True
        return  False

    target_rank     = 0 if piece.color=='red' else N-1
    
    return inner(piece.location,target_rank)