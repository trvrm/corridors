from _corridors_mcts import _corridors_mcts
from math import sqrt

class Corridors_MCTS(_corridors_mcts):
    
    """
    Class manages state of an MCTS corridors instance.
    The instance runs simulations continuously in a separate
    thread, but is interruptable to take certain actions
    via the API calls below.

    The initializer arguments (with suggesed defaults)
    are the model hyperparemeters:

    c - exploration parameter. Higher values result in wider
        trees, lower values result in deeper trees.

    seed - random seed used for generating rollouts

    min_simulations - game will not provide evaluations
        via get_sorted_actions until at least this many
        simulations have been performed

    max_simulations - simulations will stop once this number
        is reached

    sim_increment - the number of simulations performed on 
        each iteration of the event loop. reduce it if the
        API is being too slow.
    """

    def __init__(self, c=sqrt(2), seed=42, min_simulations=10000, max_simulations=1000000, sim_increment=250):
        super().__init__(c, seed, min_simulations, max_simulations, sim_increment)


        
    def __call__(board):
        import numpy as np
        assert hasattr(board,"N"), "Board must have attribute 'N'"
        assert isinstance(board.N,int), "N must be an integer"
        assert board.N==9, "Board must be 9x9"
        assert hasattr(board,'walls'), "Board must have walls attribute"
        # board has a member 'walls', a 2d numpy array
        assert isinstance(board.walls,np.ndarray), "board.walls must be numpy array"
        assert board.walls.shape==(8,8), "board.walls must be 8x8 grid"
        
        for w in board.walls.flatten:
            assert w in (0,-1,1), "each wall must be either -1 (vertical), +1 (horizontal), or zero (nonexistant)"
        
        assert hasattr(board,'turn'), "Board must have a turn attribute"
        assert board.turn in ('red','blue'), "Turn must be one of 'red', 'blue'"
        assert hasattr(board,'wallsPerPiece'), "Board must have a wallsPerPiece attribute"
        assert board.wallsPerPiece==10
        assert hasattr(board,'red'), "board must have a red piece attribute"
        assert hasattr(board,'blue'), "board must have a blue piece attribute"
        assert board.red.color=='red'
        assert board.blue.color=='blue'
        assert isinstance(board.red.walls,int), "Piece must have integer walls attribute"
        assert isinstance(board.blue.walls,int), "Piece must have integer walls attribute"
        assert 0 <=board.red.walls <=10
        assert 0 <=board.blue.walls <=10

        assert isinstance(board.red.location,tuple), "red piece must have a location"
        assert len(board.red.location)==2
        assert isinstance(board.blue.location,tuple), "blue piece must have a location"
        assert len(board.blue.location)==2
        
        assert 0 <=board.red.location[0] <=8, "red Y coordinate must be between 0 and 8"
        assert 0 <=board.red.location[1] <=8, "red X coordinate must be between 0 and 8"
        assert 0 <=board.blue.location[0] <=8, "blue Y coordinate must be between 0 and 8"
        assert 0 <=board.blue.location[1] <=8 , "blue X coordinate must be between 0 and 8"
        
        
        command = some_magic()  # implement this!
        
        assert isinstance(command,list), "I represent commands as lists"
        assert commands[0] in ("hwall","vwall","move","hop"), "not a legal command"
        all_legal_commands=list(board.allLegalCommands())
        assert command in all_legal_commands
        return command
        
        

    def display(self, flip=False):
        """Provides an ASCII representation of the board from
        heros perspective. Flip will provide the same board
        from villain's perspective."""
        return super().display(flip)

    def make_move(self, action_text, flip=False):
        """Makes a move according to the following action text:
        *(X,Y)  - move hero's token to new coordinate (X,Y)
        H(X,Y)  - place a horizontal wall at intersection (X,Y)
        V(X,Y)  - place a vertical wall at intersection (X,Y)"""
        return super().make_move(action_text,flip)
    
    def get_sorted_actions(self, flip=True):
        """Gets a list of tuples which represent all legal moves.
        List is sorted according to first value. Flip is defaulted
        to true since otherwise we'd be getting action/states from
        villain's perspective.
        Values are:
        0 - visits to state/action pair
        1 - estimated evaluation
        2 - string to describe action (i.e. what you pass to make_move to make that choice)"""
        return super().get_sorted_actions(flip)

    def choose_best_action(self, epsilon=0):
        """ make an epsilon-greedy choice """
        return super().choose_best_action(epsilon)

    def ensure_sims(self, sims):
        """ blocking function that holds until at
        least 'sims' simulations have been performed """
        return super().ensure_sims(sims)

    def get_evaluation(self):
        """ Returns -1, 1, or None, depending on whether
        a non-terminal evaluation is available for this position """
        eval = super().get_evaluation()
        return eval if eval else None

def display_sorted_actions(sorted_actions,list_size=0):
    output = ""
    output += f'Total Visits: {sum(a[0] for a in sorted_actions)}\n'
    for a in sorted_actions[:list_size if list_size else len(sorted_actions)]:
        output += f'Visit count: {a[0]} Equity: {a[1]:.4f} Action: {a[2]}\n'
    output += '\n'
    return output

def computer_self_play(p1, p2=None, stop_on_eval=False):
    """Pass one or two instances of corridors_mcts to perform self-play.
    p1 acts first"""
    if not p2: p2=p1
    p1_is_hero = True

    sorted_actions = p1.get_sorted_actions(True)
    while len(sorted_actions):
        if p1_is_hero:
            print("Hero's turn")
            hero = p1
            villain = p2
        else:
            print("Villain's turn")
            hero = p2
            villain = p1

        # display the current board state and actions
        print(hero.display(not p1_is_hero))
        print(display_sorted_actions(sorted_actions,5))

        # make action selection
        best_action = sorted_actions[0][2]

        hero.make_move(best_action,p1_is_hero)
        if hero is not villain:
            #in the 2-tree case, we have to make the same move in each tree
            villain.make_move(best_action,p1_is_hero)

        # stop early
        if stop_on_eval and hero.get_evaluation():
            print(hero.display(p1_is_hero))
            eval = hero.get_evaluation() * (-1 if p1_is_hero else 1)
            print("Hero wins!" if eval > 0 else "Villain wins!")
            break

        # prepare for next iteration
        sorted_actions = villain.get_sorted_actions(not p1_is_hero)
        hero_sorted_actions = hero.get_sorted_actions(p1_is_hero) # we don't use this, we just call (blocking) to ensure min_simulations is met
        if len(sorted_actions)==0:
            print(hero.display(p1_is_hero))
            print("Hero wins!" if p1_is_hero else "Villain wins!")

        p1_is_hero = not p1_is_hero

def human_computer_play(mcts, human_plays_first=True, hide_humans_moves=True):
    """Pass a single instance of corridors_mcts to perform computer vs human play."""
    humans_turn = human_plays_first
    sorted_actions = mcts.get_sorted_actions(humans_turn)
    while len(sorted_actions):
        print("Your turn" if humans_turn else "Computer's turn")

        # display the current board state and actions
        print(mcts.display(not humans_turn))
        if not hide_humans_moves:
            print(display_sorted_actions(sorted_actions,5))

        # make action selection
        if humans_turn:
            print("Please enter move:")
            action = input()
            while action not in (a[2] for a in sorted_actions):
                print("Illegal move!")
                action = input()
        else:
            action = sorted_actions[0][2]

        mcts.make_move(action,humans_turn)

        # prepare for next iteration
        sorted_actions = mcts.get_sorted_actions(not humans_turn)
        if len(sorted_actions)==0:
            print(hero.display(not humans_turn))
            print("Human wins!" if humans_turn else "Computer wins!")

        humans_turn = not humans_turn

if __name__ == '__main__':
    p1 = Corridors_MCTS(c=sqrt(2),seed=74)
    print("Do you want to play against the computer? No means computer self-play. (y/n)")
    if input()=="y":
        print("Please wait one moment...")
        human_computer_play(p1)
    else:
        p2 = Corridors_MCTS(seed=75)
        p1.ensure_sims(100000)
        p2.ensure_sims(100000)
        computer_self_play(p1,p2,stop_on_eval=True)