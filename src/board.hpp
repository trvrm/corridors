#pragma once


#include <list>
#include <sstream>
#include "boost/multi_array.hpp"
#include <boost/variant.hpp>

#include <set>


//not yet in C++!

template <typename T>
bool contains(const std::set<T> s, const T& v){
    return s.find(v) != s.end();
}



enum Color { RED=1,  BLUE =0};
enum Wall {EMPTY=0,HORIZONTAL=1, VERTICAL=-1};
enum Direction {UP=0x01, RIGHT=0x02, DOWN=0x04, LEFT=0x08};

std::string direction_name(Direction d);

std::string orientation_name(Wall w);
/*
    What if we made direction 0001, 0010, 0100, 1000
    1,2,4,8
    
    Then each square stores some combination of those values as walls.
    
*/

inline bool canMove(const uint square, const Direction& direction ){
    return not (square & direction) ;
}

typedef boost::multi_array<Wall, 2> walls_type;
typedef boost::multi_array<uint,2> Squares;

void apply_wall(Squares& squares, Wall orientation, uint j, uint i);

//could just be std::pair?
struct Location{
    
    uint j;
    uint i;
    Location(uint j_, uint i_):
        j(j_),
        i(i_)
    {}
        
    bool operator==(const Location& rhs) const
    {
        return i==rhs.i and j==rhs.j;
    }
    
    bool operator!=(const Location& rhs) const
    {
        return i!=rhs.i or j!=rhs.j;
    }
    
    bool operator < (const Location& rhs) const{
        return j<rhs.j or (j==rhs.j and i < rhs.i);
    }
};

inline Location locationFromDirection(const Location& location,const Direction& direction){
    uint j = location.j;
    uint i = location.i;
    switch(direction){
        case UP:    return Location(j-1,i);
        case DOWN:  return Location(j+1,i);
        case LEFT:  return Location(j,i-1);
        case RIGHT:
        default: 
                    return Location(j,i+1);
    }
}


struct WallCommand{
    Location location;
    Wall orientation;
    WallCommand(Location l, Wall o):
        location(l), orientation(o){}
};
struct HopCommand{
    Direction d1;
    Direction d2;
    HopCommand(Direction d1_, Direction d2_):
        d1(d1_),
        d2(d2_)
        {}
    
};
struct MoveCommand{
    Direction direction;
    MoveCommand(Direction d):
        direction(d)
        {}
    
};

/*
    We need an inter-language way of representing commands
    
    UP
    UP UP
    H 1 2
    V 0 0
*/


std::ostream &operator<<(std::ostream &os, WallCommand const &c);
std::ostream &operator<<(std::ostream &os, HopCommand const &c) ;
std::ostream &operator<<(std::ostream &os, MoveCommand const &c) ;

std::ostream &operator<<(std::ostream& os, Location l);
//Might be simpler to do this with py::object?
typedef boost::variant<WallCommand, MoveCommand, HopCommand> Command;



class Piece{
    
public:
    
    Color color;
    Location location;
    uint walls;
    Piece(Color c, Location l, uint w):
         color(c)
        ,location(l)
        ,walls(w)
    {}
        
    void reset(Location l){
        this->location = l;
        this->walls=10;
    }
};


struct Board{
    Piece red;
    Piece blue;
    
    walls_type walls;
    Squares squares;
    const uint N;
    Color turn;
     
    Board();
    
    // void reset();
    
    bool legalCommand(const Command& c) const;
    bool legalWall(const WallCommand& c) const;
    bool legalMove(const Piece& piece, const MoveCommand& c) const;
    bool legalMove(const Location& location, const Direction& d, bool checkPieces=true) const;
    bool legalHop(const Piece& piece, const HopCommand& c) const;
        
    
    inline Piece& currentPiece(){
        return  (RED==turn)?red:blue;
    }
    inline const Piece& currentPiece() const{
        return  (RED==turn)?red:blue;
    }
    
    inline bool gameOver() const{
        return red.location.j==0 or blue.location.j==8;
    }
    
    void apply(const Command& c);
}; 