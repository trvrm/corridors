import functools
import uuid
import json
import datetime
import contextlib
import logging

@contextlib.contextmanager
def timed():
    start=datetime.datetime.now()
    try:
        yield  
    finally:
        duration=datetime.datetime.now()-start
        logging.info(duration)
        
def default_encoder(thing):
    if isinstance(thing,uuid.UUID):
        return str(thing)
    if hasattr(thing,'__json__'):
        return thing.__json__()
    raise TypeError(repr(thing) + ' is not JSON serializable')

dumps = functools.partial(json.dumps,indent=0, sort_keys=True,ensure_ascii=False, default=default_encoder)


# Conversion to/from cpp representation
def to_python_board(c_board):
    # simplest thing might be to construct a Python board object
    from . import board  #oops, masks the name
    from ._corridors import Color
    p_board = board.Board()
    p_board.red.location = (c_board.red.location.j,c_board.red.location.i)
    p_board.blue.location= (c_board.blue.location.j, c_board.blue.location.i)
    p_board.turn = 'red' if (c_board.turn == Color.RED) else 'blue'
    
    p_board.red.walls=c_board.red.walls
    p_board.blue.walls=c_board.blue.walls
    for j in range(8):
        for i in range(8):
            p_board.walls[j,i]=c_board.walls[j,i] 
            
    return p_board
    
    
def to_cpp_board(p_board):
    from . import _corridors
    from ._corridors import Color
    
    c_board=_corridors.Board()
    c_board.red.location.j=p_board.red.location[0]
    c_board.red.location.i=p_board.red.location[1]
    c_board.blue.location.j=p_board.blue.location[0]
    c_board.blue.location.i=p_board.blue.location[1]
    c_board.red.walls=p_board.red.walls
    c_board.blue.walls=p_board.blue.walls
    
    
    for j in range(8):
        for i in range(8):
            wall = p_board.walls[j,i]
            if wall:
                c_board.place_wall(
                    _corridors.Wall(wall),j,i
                )
    
    c_board.turn = Color.RED if (p_board.turn == 'red') else Color.BLUE
    
    return c_board