#include "board.hpp"
#include "boost/optional.hpp"
class BaseBot{
public:
    virtual Command call(const Board& board);
    virtual double evaluate(const Board& board) const;
    std::vector<Command> legal_commands(const Board& board);
};


class StepsBot2 : public BaseBot{
public:
    virtual double evaluate(const Board& board) const;
};

class StepsBot3 : public BaseBot{
public:
    virtual double evaluate(const Board& board) const;
};



class AlphaBetaBot: public BaseBot{
    StepsBot3 evalbot_;
    
    uint ab_calls_;
    double alphabeta(const Board& board, uint depth, double alpha, double beta);
    boost::optional<Command> best_command_;
    const uint maxDepth_;
public:
    AlphaBetaBot(uint maxDepth=3):ab_calls_(0),maxDepth_(maxDepth){
        
    }
    
    virtual Command call(const Board& board);
    
};

int stepsToEscape(const Board& board, const Piece& location);
