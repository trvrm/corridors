import uuid
from . import board

class Game:
    def __init__(self,player):
        self.board=board.Board()
        self.uuid=str(uuid.uuid4())
        self.players={
            'red':player,
            'blue':None
        }
        
        # Eventualyl will also do clock management
        
    def __json__(self):
        return vars(self)
        
    def __repr__(self):
        return f"Game<{self.uuid}>"   