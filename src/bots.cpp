#include "bots.hpp"
#include <vector>
#include <boost/optional.hpp>
#include <list>
#include <iostream>
#include <cmath>
using std::cout; 
using std::endl;
using boost::optional;

namespace {
    //not sure how else I get an iterable?
    const std::vector<Direction> directions = {UP,RIGHT,LEFT,DOWN};
    const double inf = std::numeric_limits<double>::infinity();

}


std::vector<Command> allCommands(){
    std::vector<Command> move_commands = {
        MoveCommand(UP),
        MoveCommand(DOWN),
        MoveCommand(LEFT),
        MoveCommand(RIGHT),
    };

    std::vector<Command> hop_commands={
        HopCommand(UP,UP),HopCommand(UP,LEFT),HopCommand(UP,RIGHT),
        HopCommand(DOWN,DOWN),HopCommand(DOWN,LEFT),HopCommand(DOWN,RIGHT),
        HopCommand(LEFT,UP),HopCommand(LEFT,DOWN),HopCommand(LEFT,LEFT),
        HopCommand(RIGHT,UP),HopCommand(RIGHT,DOWN),HopCommand(RIGHT,RIGHT)
    };
    
    std::vector<Command> wall_commands;
    for(uint j=0;j<8;j++){
        for(uint i=0;i<8;i++)
        {
            wall_commands.push_back(WallCommand(Location(j,i),VERTICAL));
            wall_commands.push_back(WallCommand(Location(j,i),HORIZONTAL));
        }
    }
    
    std::vector<Command> commands;
    
    //is this correct?
    
    commands.insert(commands.end(), move_commands.begin(), move_commands.end());
    commands.insert(commands.end(), hop_commands.begin(), hop_commands.end());
    commands.insert(commands.end(), wall_commands.begin(), wall_commands.end());
    return commands;
}

//only want to calculate this once!
std::vector<Command> ALL_COMMANDS=allCommands();


Board apply(const Board& board, const Command& command){
    Board copy = board; // probably need a copy constructor?
    copy.apply(command);
    return copy;
    
}

std::vector<Command> BaseBot::legal_commands(const Board& board){
    std::vector<Command> legalCommands;

    std::copy_if (
        ALL_COMMANDS.begin(), 
        ALL_COMMANDS.end(), 
        std::back_inserter(legalCommands), 
        [&board](const Command& c){
            return board.legalCommand(c);
        } 
    );
    return legalCommands;
}

double BaseBot::evaluate(const Board& board) const{
    throw std::runtime_error("Don't call BaseBot::evaluate");
}

Command BaseBot::call(const Board& board){
    
    std::vector<Command> legalCommands=legal_commands(board);
    
    if (legalCommands.size()==0){
        throw std::runtime_error("No legal commands left");
    }
    Command best_command=legalCommands.at(0);
    bool maximize = board.turn==RED;
    double best_score=maximize?-999999:999999;
    
    for(auto const& command: legalCommands){
        const Board child = apply(board,command);
 
        double score = this->evaluate(child);
        
        if (maximize){
            if (score>=best_score){
                best_command=command;
                best_score=score;
            }
        }
        else{
            if (score<best_score){
                best_command=command;
                best_score=score;
            }
        }
     
    }
    return best_command;
}

double StepsBot2::evaluate(const Board& board) const{
    double inf = std::numeric_limits<double>::infinity();
    if (board.red.location.j==0)  return inf;
    if (board.blue.location.j==8) return -inf;
    
    double r  = 0.5+  stepsToEscape(board,board.red);
    double b  = 0.5+  stepsToEscape(board,board.blue);
    return (r<b)?( b/r -1):(1 -(r/b));
}


double StepsBot3::evaluate(const Board& board) const{
    
    
    //I want it allergic to a very high wall diff
    double diff = (board.red.walls-board.blue.walls)/4;
    double wall_score = diff*diff*diff; // how do we cube stuff in C++
    
    
    uint red_distance  = 1+stepsToEscape(board,board.red);
    uint blue_distance = 1+stepsToEscape(board,board.blue);
    
    if(board.turn==RED)
        blue_distance+=1;
    else
        red_distance+=1;
    double difference = log(blue_distance)-log(red_distance);
    
    return difference+ wall_score;
}


int stepsToEscape(const Board& board, const Piece& piece){
    const Squares squares = board.squares;
    
    
    boost::multi_array<bool,2> checked(boost::extents[9][9]);
    std::fill_n(checked.data(),   checked.num_elements(), false);
    
    uint target_rank = piece.color==RED?0:8;
    
    std::set<Location> neighbours;
    for(uint i=0;i<9;i++)
        neighbours.insert(Location(target_rank,i));
    
    uint steps = 0;
    
    
    for(auto it=0;it<81;it++){
        for(auto const& neighbour: neighbours){
            
            checked[neighbour.j][neighbour.i]=true;
            if (neighbour==piece.location) return steps;
        }
        
        //rebuild neighbours...
        std::set<Location> n2;
        for(auto const& neighbour: neighbours){
            const uint square = squares[neighbour.j][neighbour.i];
            for(auto const& direction: directions) {
                if (canMove(square,direction)){
                    const Location target = locationFromDirection(neighbour,direction);
                    if (not checked[target.j][target.i]){
                        n2.insert(target);
                    }
                }
                
            }
        }
        neighbours=n2;
        steps+=1;
        
    }
    //this is a problem
    throw std::runtime_error("no way out");
    
}



Command AlphaBetaBot::call(const Board& board){
    this->ab_calls=0;
    uint maxDepth=3; //was THREE
    
    best_command_ = boost::optional<Command>();
    
    this->alphabeta(board,maxDepth,-inf,inf);
    
    if(not best_command_)
        throw std::runtime_error("Couldn't compute a command");
    return *best_command_;
}

const uint MAX_AB_CALLS=20000;
double AlphaBetaBot::alphabeta(const Board& board, uint depth, double alpha, double beta){
    
    if(depth==0)
        return evalbot_.evaluate(board);
    if (board.gameOver())
        return evalbot_.evaluate(board);
        
    this->ab_calls+=1;
    
    std::vector<Command> legalCommands=legal_commands(board);
    //If we don't have any legal commands, we're kinda screwed
    
    if (legalCommands.size()==0){
        std::stringstream s;
        s << "No legal commands left for AlphaBetaBot to evaluate.  Depth is " << depth << ", ab_calls is " << ab_calls
            << "turn is " << board.turn;
        throw std::runtime_error(s.str());
    }
    
    if (board.turn==RED){
        double v = -inf;
        Command best_command=legalCommands.at(0);
        
        for(auto const& command: legalCommands){
            Board child = apply(board,command);
            double score = alphabeta(child,depth-1,alpha,beta);
            if (score > v){
                v=score;
                best_command=command;
            }
            alpha=std::max(alpha,v);
            if (beta<=alpha)
                break;
            if (ab_calls>=MAX_AB_CALLS){
                std::cout << "MAX_AB_CALLS" << endl;
                break;
            }
        }
        best_command_=best_command;
        return v;
    }
    else{ // BLUE
        double v = inf;
        Command best_command=legalCommands.at(0);
        for(auto const& command: legalCommands){
            Board child = apply(board,command);
            double score = alphabeta(child,depth-1,alpha,beta);
            if(score<v){
                v=score;
                best_command=command;
            }
            beta=std::min(beta,v);
            if(beta<=alpha)
                break;
            if (ab_calls>=MAX_AB_CALLS){
                std::cout << "MAX_AB_CALLS" << endl;
                break;
            }
        }
        best_command_=best_command;
        return v;
    }
    
}