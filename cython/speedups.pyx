# coding: utf-8
# cython: profile=False

'''
    Currently getting a 6x speedup, not nearly enough!
'''
cimport cython

import numpy as np


DTYPE = np.intc

 
cdef int EMPTY      = 0
cdef int HORIZONTAL = 1
cdef int VERTICAL   = -1

cdef int UP    = 0
cdef int DOWN  = 1
cdef int LEFT  = 2
cdef int RIGHT = 3

@cython.boundscheck(False)  # Deactivate bounds checking
@cython.wraparound(False)   # Deactivate negative indexing.
cdef inline int canMove(int [:, :] walls,Py_ssize_t j, Py_ssize_t i, int direction):
    cdef int M=8
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



@cython.boundscheck(False)  # Deactivate bounds checking
@cython.wraparound(False)   # Deactivate negative indexing.
cdef inline int _canEscape(Py_ssize_t j, Py_ssize_t i, int target_rank,int [:, :] checked_squares, int [:, :] walls):
    '''
        This is now highly optimized
    '''
    cdef int N = 9
    cdef int checked = 1
    
    if j<0:return 0
    if i<0: return 0
    if i>=N: return 0
    if j>=N: return 0
    
    if checked_squares[j,i]:        return 0
    if j==target_rank:              return 1
    
    
    checked_squares[j,i]=checked
    
    if canMove(walls,j,i,UP):
        if _canEscape(j-1,i,target_rank,checked_squares,walls):
            return True
        
    if canMove(walls,j,i,DOWN):
        if _canEscape(j+1,i,target_rank,checked_squares,walls):
            return True
        
    if canMove(walls,j,i,LEFT):
        if _canEscape(j,i-1,target_rank,checked_squares,walls):
            return True
                
    if canMove(walls,j,i,RIGHT):
        if _canEscape(j,i+1,target_rank,checked_squares,walls):
            return True
        
    return False


def canEscape(board,piece):
    cdef int N = 9

    cdef int [:, :] walls_view = board.walls #.astype(np.int32)
    #cdef checked_squares = set()
    # could be a numpy grid
    cdef int unchecked = 0
    
    cdef int [:, :] checked_squares = np.full((N,N),unchecked, dtype=DTYPE)
    
    cdef int target_rank     = 0 if piece.color=='red' else N-1
    
    cdef int j=piece.location[0]
    cdef int i=piece.location[1]
    
    return bool(_canEscape(j,i,target_rank, checked_squares, walls_view))
  
  


@cython.boundscheck(False)  # Deactivate bounds checking
@cython.wraparound(False)   # Deactivate negative indexing.
def stepsToEscape(board,piece):
    
    cdef Py_ssize_t tj, ti, j, i, piece_j, piece_i
    cdef int N = board.N
    cdef int M = N-1
    cdef int [:, :] walls = board.walls
    cdef int unchecked=-1
    
    squares_ = np.full((N,N),unchecked, dtype=DTYPE)
    cdef int [:, :] squares = squares_
    
    cdef int target_rank = 0 if piece.color=='red' else N-1
    
    # Is there a faster data type I can use here?
    cdef set neighbours={(target_rank,i) for i in range(N)}
    
    cdef int steps=0
    
    location=piece.location
    cdef list directions= [UP,DOWN,LEFT,RIGHT]
    
    for it in range(N**2):
        for (j,i) in neighbours:
            squares[j,i]=steps          # mark
            if (j,i)==location:# check
                return steps
        
        
        # this is almost certainly the biggest bottleneck.
        neighbours = {
            (tj,ti)
            for (j,i) in neighbours
            for direction,  (tj,ti) in [ (UP,(j-1,i)),(DOWN,(j+1,i)),(LEFT,(j,i-1)),(RIGHT,(j,i+1))]
            if canMove(walls, j, i, direction)
            if (squares[tj,ti]) == unchecked
        }
        
        steps+=1
        
    assert 0, "no way out"
    
    
    
def legalWall(int [:, :] walls, int j, int i, int orientation):
    cdef int N = 9
    cdef int M = 8
    
    
    # assert 0<=j<M
    # assert 0<=i<M
    # 
    # assert orientation in (HORIZONTAL,VERTICAL), orientation
    # 
    if orientation == HORIZONTAL:
        if walls[j,i]:                    return False
        if i>0   and walls[j,i-1]==HORIZONTAL: return False
        if i<M-1 and walls[j,i+1]==HORIZONTAL: return False
    if orientation == VERTICAL:
        if walls[j,i]:                    return False
        if j>0   and walls[j-1,i]==VERTICAL:   return False
        if j<M-1 and walls[j+1,i]==VERTICAL:   return False
    
    return True
    
    