# coding: utf-8
# cython: profile=True

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
cdef inline int canMove(int M,int [:, :] walls,Py_ssize_t j, Py_ssize_t i, int direction):
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

cdef int inner(tuple location, int target_rank,set checked_squares,int M, int [:, :] walls):
    
    cdef int j = location[0]
    cdef int i = location[1]
    if j==target_rank:              return True
    
    if location in checked_squares: return False
    checked_squares.add(location)
    
    for direction,  target in ( (UP,(j-1,i)),(DOWN,(j+1,i)),(LEFT,(j,i-1)),(RIGHT,(j,i+1))):
        if target not in checked_squares:
            if canMove(M, walls,j,i,direction):
                if inner(target,target_rank,checked_squares,M,walls):
                    return True
    return  False


def canEscape(board,piece):
    cdef int N = board.N
    cdef int [:, :] walls_view = board.walls #.astype(np.int32)
    cdef checked_squares = set()
    cdef int target_rank     = 0 if piece.color=='red' else N-1
    cdef int M = N-1
    return bool(inner(piece.location,target_rank, checked_squares,M, walls_view))
  
  


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
            if canMove(M, walls, j, i, direction)
            if (squares[tj,ti]) == unchecked
        }
        
        steps+=1
        
    assert 0, "no way out"
    