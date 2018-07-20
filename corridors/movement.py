import numpy as np

from . import config

from .movement_python import EMPTY, HORIZONTAL,VERTICAL,UP,DOWN,LEFT,RIGHT
if config.USE_SPEEDUPS:
    from .speedups import stepsToEscape, canEscape
    
    print('speedups installed')
else:
    from .movement_python import stepsToEscape, canEscape
    
    print('no speedups installed')