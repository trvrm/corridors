import logging
import sys

def configureLogging():
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(name)8s: %(message)s',
        stream=sys.stdout,
    )
    
    
    
# One of cython, pybind, none
SPEEDUPS=''
SPEEDUPS='cython'
#SPEEDUPS='cython'
