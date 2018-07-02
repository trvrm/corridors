import uuid
import names
from . import board

class User:
    '''
        Human player.
    '''
    def __init__(self):
        self.uuid=uuid.uuid4()
        
        self.name=names.get_first_name()
        
        
    def __str__(self):
        return self.name
    def __repr__(self):
        return f"User ({self.name}:{self.uuid})"

    def __json__(self):
        return {
            'name':self.name,
            'uuid':self.uuid
        }
        
class Game:
    '''
        Is it a mistake to have separate 'game' and 'board' classes?
    '''
    def __init__(self,red):
        self.board=board.Board()
        self.uuid=str(uuid.uuid4())
        self.players={
            'red':red,
            'blue':None
        }
        
        # one of (hwall, vwall, piece, None)
        self.selected=None
        
        # Eventualyl will also do clock management
        
    def __json__(self):
        return {
            'board':self.board,
            'uuid':self.uuid,
            'players':self.players,
            'over':self.board.gameOver(),
            'winner':self.board.winner(),
            'selected':self.selected
        }
        return vars(self)
        
    def __repr__(self):
        return f"Game<{self.uuid}>"   