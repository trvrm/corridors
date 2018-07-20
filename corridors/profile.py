# unit tests
import corridors
import corridors.board
import corridors.board
import corridors.utilities
import corridors.bots
import datetime
import contextlib

@contextlib.contextmanager
def timed():
    start=datetime.datetime.now()
    try:
        yield  
    finally:
        duration=datetime.datetime.now()-start
        print(duration)
     

def test_speed():
    '''
        I recall this should take about 30 seconds.
        I'm not sure why it's taking much longer.
    '''
    with timed():
        b=corridors.board.Board()
        evalbot=corridors.bots.StepsBot2()
        bot=corridors.bots.AlphaBetaBot(evalbot,maxDepth=1)
        
        move=bot(b)
        print(move)

            
if __name__=='__main__':
    
    test_speed()