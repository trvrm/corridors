from .bots import BaseBot
from . import board
from . import _corridors
from .utilities import to_cpp_board
from .profile import timed

class CPPAlphaBetaBot(BaseBot):
    def __init__(self):
        self.c_bot=_corridors.AlphaBetaBot()
        
    def __call__(self,p_board):
        c_board=to_cpp_board(p_board)
        try:
            with timed():
                c_command =  self.c_bot.call(c_board)
        except Exception as e:
            
            print('exception evaluating board')
            print(c_board)
            raise
        # print(c_command)
        
        c_command=c_command.to_tuple()
        # print(c_command)
        if c_command[0]=='h':
            p_command = ['hwall',(c_command[1],c_command[2])]
        if c_command[0]=='v':
            p_command = ['vwall',(c_command[1],c_command[2])]
            
        if len(c_command)==1:
            p_command =  ['move',c_command[0]]
        if len(c_command)==2:
            p_command= ['hop',c_command[0],c_command[1]]
            
        
        assert p_command in board.boardCommands(9), "Not a real command: {}".format(p_command)
        
        legal = list(p_board.allLegalCommands())
        if p_command not in legal:
            print(p_board)
            print(p_command)
            print(c_board)
            print("CPPAlphaBetaBot suggested an illegal command: {}".format(p_command))
            assert 0
        
        return p_command