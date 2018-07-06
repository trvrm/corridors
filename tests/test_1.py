# unit tests
import corridors
import corridors.board
import corridors.utilities

from corridors import names
# how the hell is this passing?

def test_1():
    board=corridors.board.Board()
    board.allLegalCommands()
    
def test_json_dump():
    
    board=corridors.board.Board()
    corridors.utilities.dumps(board)

def test_version():
    assert corridors.__version__>='0.0.1'
    
def test_names():
    assert corridors.names
    assert 0, names