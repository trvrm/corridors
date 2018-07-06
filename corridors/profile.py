# unit tests
import corridors
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
        bot=corridors.bots.StepsBot()
        
        
        while not b.gameOver():
            
            move=bot(b)
            print(move)
            b(*move)
        print(b.winner())
if __name__=='__main__':
    
    test_speed()