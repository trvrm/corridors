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
    
    with timed():
        b=corridors.board.Board()
        sbot=corridors.bots.StepsBot2()
        bot=corridors.bots.AlphaBetaBot(sbot)
        
        for i in range(5):
            move=bot(b)
            print(move)
            b(*move)
            
if __name__=='__main__':
    
    test_speed()