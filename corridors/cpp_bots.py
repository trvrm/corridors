from .bots import BaseBot
from . import board
from . import _corridors

from .profile import timed
from .corridors_mcts import Corridors_MCTS

# Conversion to/from cpp representation
def to_python_board(c_board):
    from . import board
    from ._corridors import Color

    p_board = board.Board()
    p_board.red.location = (c_board.red.location.j, c_board.red.location.i)
    p_board.blue.location = (c_board.blue.location.j, c_board.blue.location.i)
    p_board.turn = "red" if (c_board.turn == Color.RED) else "blue"

    p_board.red.walls = c_board.red.walls
    p_board.blue.walls = c_board.blue.walls
    for j in range(8):
        for i in range(8):
            p_board.walls[j, i] = c_board.walls[j, i]

    return p_board


def to_cpp_board(p_board):
    from . import _corridors
    from ._corridors import Color

    c_board = _corridors.Board()
    c_board.red.location.j = p_board.red.location[0]
    c_board.red.location.i = p_board.red.location[1]
    c_board.blue.location.j = p_board.blue.location[0]
    c_board.blue.location.i = p_board.blue.location[1]
    c_board.red.walls = p_board.red.walls
    c_board.blue.walls = p_board.blue.walls

    for j in range(8):
        for i in range(8):
            wall = p_board.walls[j, i]
            if wall:
                c_board.place_wall(_corridors.Wall(wall), j, i)

    c_board.turn = Color.RED if (p_board.turn == "red") else Color.BLUE

    return c_board


class CPPBotWrapper(BaseBot):
    def __init__(self, cpp_bot):
        self.c_bot = cpp_bot
        # self.c_bot=_corridors.AlphaBetaBot()

    def __call__(self, p_board):
        c_board = to_cpp_board(p_board)
        try:
            with timed():
                c_command = self.c_bot.call(c_board)
        except Exception as e:

            print("exception evaluating board")
            print(c_board)
            raise
        # print(c_command)

        c_command = c_command.to_tuple()
        # print(c_command)
        if c_command[0] == "h":
            p_command = ["hwall", (c_command[1], c_command[2])]
        if c_command[0] == "v":
            p_command = ["vwall", (c_command[1], c_command[2])]

        if len(c_command) == 1:
            p_command = ["move", c_command[0]]
        if len(c_command) == 2:
            p_command = ["hop", c_command[0], c_command[1]]

        assert p_command in board.boardCommands(9), "Not a real command: {}".format(
            p_command
        )

        legal = list(p_board.allLegalCommands())
        if p_command not in legal:
            print(p_board)
            print(p_command)
            print(c_board)
            print("CPPAlphaBetaBot suggested an illegal command: {}".format(p_command))
            assert 0

        return p_command


class CPPStepsBot(CPPBotWrapper):
    def __init__(self):
        super().__init__(_corridors.StepsBot2())


class CPPAlphaBetaBot(CPPBotWrapper):
    def __init__(self,max_depth):
        super().__init__(_corridors.AlphaBetaBot(max_depth))
        
        
class MCTSBot(BaseBot):
    def __init__(self):
        self.c_bot=Corridors_MCTS(
            min_simulations=1000,
            max_simulations=10000
        )
            
    def __call__(self, board):
        return self.c_bot(board)
