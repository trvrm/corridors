#include <pybind11/pybind11.h>
#include <iostream>
#include <list>
#include <exception>
#include <sstream>
#include "boost/multi_array.hpp"
#include "boost/variant.hpp"

#include "board.hpp"
#include "bots.hpp"
namespace py = pybind11;

// 
// void apply_wall_command(Board& board, WallCommand& c){
//     if(!board.legalWall(c))
//     {
//         std::stringstream s;
//         s << "Illegal wall command requested: " << c;
//         throw std::runtime_error(s.str());
//     }
// 
//     board.apply(c);    
// }

void place_wall(Board& board, Wall orientation, uint j, uint i){
    /*
        For manually constructing a board; doesn't check anything
        or decrement wall count
    */
    board.walls[j][i]=orientation;
    apply_wall(board. squares, orientation,j,i);
}


class tuple_visitor : public boost::static_visitor<py::tuple>
{
public:
    py::tuple operator()(const WallCommand& c) const {
        std::string orientation = c.orientation==HORIZONTAL?"h":"v";
        
        return py::make_tuple(orientation,c.location.j,c.location.i);
     }
    py::tuple operator()(const MoveCommand& c) const { 
        return py::make_tuple(direction_name(c.direction));
    }
    py::tuple operator()(const HopCommand& c) const {
        return py::make_tuple(direction_name(c.d1),direction_name(c.d2));
         
    }
};

py::tuple command_to_tuple(const Command& command){
    return boost::apply_visitor(tuple_visitor(),command);
}

//very nice
//auto my_lambda = [](const Pet &a) { return "<example.Pet named '" + a.name + "'>";}; 

std::string repr_command(const Command& c){
    std::stringstream s;
    s << c;
    return s.str();
}

PYBIND11_MODULE(_corridors,m) {



#ifdef VERSION_INFO
    m.attr("__version__") = py::str(VERSION_INFO);
#else
    m.attr("__version__") = py::str("dev");
#endif

    

    
    py::enum_<Color>(m,"Color")
        .value("RED",Color::RED)
        .value("BLUE",Color::BLUE)
        .export_values()
    ;
    py::enum_<Wall>(m, "Wall")
        .value("EMPTY", Wall::EMPTY)
        .value("HORIZONTAL", Wall::HORIZONTAL)
        .value("VERTICAL", Wall::VERTICAL)
        .export_values();
        
    
        
    py::class_<walls_type>(m, "Walls")
        .def("__repr__",[](const walls_type &w){return "some walls";})
        .def("__getitem__",[](const walls_type &w, py::tuple key){
            int j = key[0].cast<int>();
            int i = key[1].cast<int>();
            
            //really need bounds checking here!
            return w[j][i];
        })
        .def("__setitem__",[](walls_type &w, py::tuple key, Wall value){
            //not good enough - need a 'set wall' function
            int j = key[0].cast<int>();
            int i = key[1].cast<int>();
            w[j][i] = value;
        })
    //Ideally I'd have some kind of slice function t
    ;
    py::class_<Location>(m,"Location")
        .def(py::init<uint, uint>())
        .def_readwrite("j", &Location::j)
        .def_readwrite("i", &Location::i)
    ;
    
    py::class_<Command>(m,"Command")
        .def("__repr__",&repr_command)
        .def("to_tuple",&command_to_tuple)
    ;
    
    py::class_<WallCommand>(m,"WallCommand")
        .def(py::init<Location,Wall>())
        .def_readonly("location",&WallCommand::location)
        .def_readonly("orientation",&WallCommand::orientation)
    ;
    
    py::class_<Piece>(m,"Piece")
        .def(py::init<Color,Location,uint>())
        .def_readonly("color",&Piece::color)
        .def_readwrite("location",&Piece::location)
        .def_readwrite("walls",&Piece::walls)
    ;
    
    
    
    py::class_<Board>(m, "Board")
        .def(py::init<>())
        .def("apply",&Board::apply)
        .def("gameOver",&Board::gameOver)
        .def("legalCommand",&Board::legalCommand)
        .def_readonly("N", &Board::N)
        .def_readwrite("turn",&Board::turn)
        .def_readonly("walls", &Board::walls)
        .def_readwrite("red",&Board::red)
        .def_readwrite("blue",&Board::blue)
        .def("place_wall",&place_wall)
        
    ;
    
    py::class_<StepsBot2>(m,"StepsBot2")
        .def(py::init<>())
        .def("evaluate",&StepsBot2::evaluate)
        .def("call",&StepsBot2::call)
    ;
    
    
    
    py::class_<AlphaBetaBot>(m,"AlphaBetaBot")
        .def(py::init<uint>())
        .def("call",&AlphaBetaBot::call)
    ;
    
    m.def("stepsToEscape", &stepsToEscape);

    // m.def("apply_wall_command", &apply_wall_command);
    
    // return m.ptr();
}

