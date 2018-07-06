'''
    Stuff that will eventually be serialized.
'''

class SharedState:
    def __init__(self):
        self.sockets=[]
        
        # Eventually these will be serialized
        self.games=[]
        self.users=[]
        
    def flush(self):
        self.sockets=[
            s for s in self.sockets
            if not s.closed
        ]
        
    def game_list(self):
        return [
            {
                'uuid':game.uuid,
                'players':game.players,
                'turn':game.board.turn,
            }
            for game in self.games
            if not game.board.gameOver()
        ][-10:]  # or whatever
        # should we flush out old games?
    def game_by_uuid(self,uuid):
        games=[g for g in self.games if g.uuid==uuid]
        if games:
            return games[0]
            
            
    def sockets_for_game(self,uuid):
        return [
            s
            for s in self.sockets
            if hasattr(s,'game')
            if s.game.uuid==uuid
        ]
            