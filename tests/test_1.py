# unit tests
import corridors
import corridors.board
import corridors.utilities
def test_1():
    board=corridors.board.Board()
    board.allLegalCommands()
    
def test_json_dump():
    
    board=corridors.board.Board()
    corridors.utilities.dumps(board)
    