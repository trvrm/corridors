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


SHAPE_N=(9,9)


from libcpp.vector cimport vector as cpp_vector
from libcpp.utility cimport pair as cpp_pair

from cython.operator cimport dereference as deref, preincrement as inc

ctypedef cpp_pair[Py_ssize_t,Py_ssize_t] LOCATION

ctypedef cpp_vector[LOCATION] LOCATIONS
ctypedef cpp_vector[LOCATION].iterator ITERATOR


@cython.boundscheck(False)  # Deactivate bounds checking
@cython.wraparound(False)   # Deactivate negative indexing.
cdef inline int _canMove(int [:, :] walls,Py_ssize_t j, Py_ssize_t i, int direction):
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

def canMove(int [:, :] walls,Py_ssize_t j, Py_ssize_t i, int direction):
    return _canMove(walls,j,i,direction)

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
    
    if _canMove(walls,j,i,UP):
        if _canEscape(j-1,i,target_rank,checked_squares,walls):
            return True
        
    if _canMove(walls,j,i,DOWN):
        if _canEscape(j+1,i,target_rank,checked_squares,walls):
            return True
        
    if _canMove(walls,j,i,LEFT):
        if _canEscape(j,i-1,target_rank,checked_squares,walls):
            return True
                
    if _canMove(walls,j,i,RIGHT):
        if _canEscape(j,i+1,target_rank,checked_squares,walls):
            return True
        
    return False




def canEscape(board,piece):
    cdef int N = 9
    cdef int [:, :] walls_view = board.walls #.astype(np.int32)
    cdef int unchecked = 0
    cdef int [:, :] checked_squares = np.full(SHAPE_N,unchecked, dtype=DTYPE)
    cdef int target_rank     = 0 if piece.color=='red' else N-1
    
    cdef Py_ssize_t j=piece.location[0]
    cdef Py_ssize_t i=piece.location[1]
    
    return bool(_canEscape(j,i,target_rank, checked_squares, walls_view))
  
  

    
    

@cython.boundscheck(False)  # Deactivate bounds checking
@cython.wraparound(False)   # Deactivate negative indexing.
def stepsToEscape(board,piece):
    
    cdef Py_ssize_t j, i, piece_j, piece_i
    cdef int N = board.N
    cdef int M = N-1
    cdef int [:, :] walls = board.walls
    cdef int unchecked=-1
    piece_j,piece_i=piece.location
    
    
    cdef int [:, :] squares = np.full((N,N),unchecked, dtype=DTYPE)
    cdef int target_rank = 0 if piece.color=='red' else N-1
    
    # fast exit:
    if target_rank==piece_j:
        return 0
    
    # Is there a faster data type I can use here?
    # cdef list neighbours=[(target_rank,i) for i in range(N)]
    # cdef list n2=[]
    cdef int steps=0
    
    cdef LOCATIONS locations=LOCATIONS()
    cdef LOCATIONS locations2
    for i in range(N):
        locations.push_back(LOCATION(target_rank,i))
    
    
    cdef ITERATOR it
    cdef int passes
    
    for passes in range(N**2):
        
        # n2=[]
        steps+=1
        
        it = locations.begin()
        while it!=locations.end():
            j=deref(it).first
            i=deref(it).second
            inc(it)
            #it++
        
        #for (j,i) in neighbours:  # this line is slow
        
        #for (j,i) in locations:
            #j=it.first
            #i=it.second
        #it = locations.begin()
        #while it != locations.end():
            
            if _canMove(walls,j,i,UP):
                if ((j-1)==piece_j) and (i==piece_i): return steps
                if squares[j-1,i]==unchecked:
                    # n2.append((j-1,i))
                    locations2.push_back(LOCATION((j-1),i))
                    squares[j-1,i]=steps
            if _canMove(walls,j,i,DOWN):
                if ((j+1)==piece_j) and (i==piece_i): return steps
                if squares[j+1,i]==unchecked:
                    # n2.append((j+1,i))
                    locations2.push_back(LOCATION((j+1),i))
                    squares[j+1,i]=steps
            if _canMove(walls,j,i,LEFT):
                if (j==piece_j) and ((i-1)==piece_i): return steps
                if squares[j,i-1]==unchecked:
                    # n2.append((j,i-1))
                    locations2.push_back(LOCATION(j,(i-1)))
                    squares[j,i-1]=steps
            if _canMove(walls,j,i,RIGHT):
                if (j==piece_j) and ((i+1)==piece_i): return steps
                if squares[j,i+1]==unchecked:
                    # n2.append((j,i+1))
                    locations2.push_back(LOCATION(j,(i+1)))
                    squares[j,i+1]=steps
        
        locations=locations2
        # neighbours=n2
        
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
    
    