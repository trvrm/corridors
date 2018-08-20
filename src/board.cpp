#include "board.hpp"
#include <set>
#include <iostream>
using std::cout;
using std::endl;

namespace {
    //not sure how else I get an iterable?
    std::vector<Direction> directions = {UP,RIGHT,LEFT,DOWN};
}


std::string direction_name(Direction d){
    switch(d){
        case UP:   return "up";
        case RIGHT:return "right";
        case LEFT: return "left";
        default:   return "down";
    }
}

std::string orientation_name(Wall w){
    switch(w){
        case HORIZONTAL: return "h";
        case VERTICAL: return "v";
        default: 
            throw std::runtime_error("Bad orientation");
    }
}

std::ostream &operator<<(std::ostream &os, WallCommand const &c) { 
    return os << "WALL "  << orientation_name(c.orientation) << "," << c.location.j << "," << c.location.i;
}
std::ostream &operator<<(std::ostream &os, HopCommand const &c) { 
    return os << direction_name(c.d1) << "," << direction_name(c.d2);
}
std::ostream &operator<<(std::ostream &os, MoveCommand const &c) { 
    return os << direction_name(c.direction);
}

std::ostream &operator<<(std::ostream& os, Location l){
    return os << "(" << l.j << "," << l.i << ")";
}


Board::Board():
     red(RED,  Location(8,5),10)
    ,blue(BLUE,Location(0,5),10)
    ,walls(boost::extents[8][8])
    ,squares(boost::extents[9][9])
    ,N(9)
    ,turn(RED)
{
    std::fill_n(walls.data(),   walls.num_elements(), EMPTY);
    std::fill_n(squares.data(), squares.num_elements(), 0);
    
    //now apply external boundaries to walls
    for(uint i=0;i<9;i++){
        squares[0][i] |= UP;
        squares[8][i] |= DOWN;
    }
    
    for(uint j=0;j<9;j++){
        squares[j][0] |= LEFT;
        squares[j][8] |= RIGHT;
    }
}

class legality_visitor : public boost::static_visitor<bool>{
    const Board& board_;
public:
    legality_visitor(const Board& board):board_(board){}
    
    bool operator()(const WallCommand& c) const{
        return board_.legalWall(c);
    }
    bool operator()(const MoveCommand& c) const{
        Piece piece = board_.currentPiece();
        return board_.legalMove(piece,c);
    }
    bool operator()(const HopCommand& c) const{
        Piece piece = board_.currentPiece();
        return board_.legalHop(piece,c);
    }
};

bool Board::legalCommand(const Command& command) const{
    if (gameOver()) return false;
    return boost::apply_visitor( legality_visitor(*this), command);
}


bool canEscape(const Squares& squares, const Location& location, const uint target_rank, boost::multi_array<bool,2>& ignore){
    
    if (location.j==target_rank) return true;
    
    if (ignore[location.j][location.i]) return false;
    ignore[location.j][location.i]=true;
    const uint square = squares[location.j][location.i];
    
    for(auto const& direction: directions) {
        if (canMove(square,direction)){
            Location target = locationFromDirection(location,direction);
            if (canEscape(squares,target,target_rank,ignore)){
                return true;
            }
        }
    }
    return false;
}

bool canEscape(const Squares& squares, const Piece& piece){
    boost::multi_array<bool,2> ignore(boost::extents[9][9]);
    std::fill_n(ignore.data(),   ignore.num_elements(), false);
    
    
    uint target_rank = piece.color==RED?0:8; 
    return canEscape(squares, piece.location, target_rank, ignore);
}

void apply_wall(Squares& squares, Wall orientation, uint j, uint i){
    if (orientation==HORIZONTAL){
        squares[j][i]      |=  DOWN;
        squares[j][i+1]    |=  DOWN;
        squares[j+1][i]    |=  UP;
        squares[j+=1][i+1] |=  UP;
    }
    else{
        squares[j][i]       |= RIGHT;
        squares[j+1][i]     |= RIGHT;
        squares[j][i+1]     |= LEFT;
        squares[j+1][i+1]   |= LEFT;
    }
}
void apply_wall(Squares& squares, const WallCommand& c){
    apply_wall(squares, c.orientation, c.location.j,c.location.i);
}
bool Board::legalWall(const WallCommand& c) const {

    const uint M = 8;
    if (not currentPiece().walls) return 0;
    
    uint j=c.location.j;
    uint i = c.location.i;
    if (walls[j][i]) return false;
    if (c.orientation==HORIZONTAL){
        if (i>0   and walls[j][i-1]==HORIZONTAL) return false;
        if (i<M-1 and walls[j][i+1]==HORIZONTAL) return false;
    }
    if (c.orientation==VERTICAL){
        if (j>0   and walls[j-1][i]==VERTICAL)   return false;
        if (j<M-1 and walls[j+1][i]==VERTICAL)   return false;
    }

    Squares tmp_squares(this->squares);

    apply_wall(tmp_squares,c);
    
    return  canEscape(tmp_squares, this->red) and canEscape(tmp_squares, this->blue);
    
}


bool Board::legalMove(const Piece& piece, const MoveCommand& c) const {
    
    return legalMove(
        piece.location,
        c.direction,
        true
    );
}

bool Board::legalMove(const Location& location, const Direction& direction, bool checkPieces) const{

    uint j=location.j;
    uint i = location.i;
    uint square = this->squares[j][i];
    
    if (square & direction) return false;

    if (checkPieces){
        Location target = locationFromDirection(location,direction);
        if (red.location==target or blue.location==target) return false;
    }

    return true;    
}

inline bool perpendicular(Direction d1, Direction d2){
    if (d1==UP or d1==DOWN)
        return (d2==LEFT or d2==RIGHT);
    else
        return (d2==UP or d2==DOWN);
}

bool Board::legalHop(const Piece& piece, const HopCommand& c) const {
    Location l1 = locationFromDirection(piece.location,c.d1);
    
    // square described by l1 MUST contain a piece.
    if (red.location!=l1 and blue.location!=l1) return false;
    
    // must be able to move to l1
    if (not legalMove(piece.location,c.d1,false)) return false;
    
    // if we CAN continue in the same direction, we MUST
    if (legalMove(l1,c.d1))
        return c.d2==c.d1;
    else
        // else d2 must be perpendicular to d1 AND
        // d1->d2 must be legal    
        return perpendicular(c.d1,c.d2) and legalMove(l1,c.d2);
}

class command_visitor : public boost::static_visitor<>
{
    Board& board_;
public:
    command_visitor(Board& board):board_(board){
        
    }
    void operator()(const WallCommand& c) const
    {
        /*
            For fast lookups we store both 
            the location of each wall AND the 
            way that it affects each square
        */
        Piece& piece=board_.currentPiece();
        board_.walls[c.location.j][c.location.i]=c.orientation;
        
        //now set walls on the four affected squares
        apply_wall(board_.squares,c);
        piece.walls-=1;
    }
    
    void operator()(const MoveCommand& c) const
    {
        Piece& piece=board_.currentPiece();
        piece.location = locationFromDirection(piece.location,c.direction);
        
    }
    void operator()(const HopCommand& c) const
    {
        Piece& piece=board_.currentPiece();
        piece.location = locationFromDirection(piece.location,c.d1);
        piece.location = locationFromDirection(piece.location,c.d2);
    }
};

void Board::apply(const Command& command){
    
    boost::apply_visitor( command_visitor(*this), command);
    this->turn = (this->turn==BLUE)?RED:BLUE;
}