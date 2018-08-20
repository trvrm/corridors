import logging
import sys

def configureLogging():
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(name)8s: %(message)s',
        stream=sys.stdout,
    )
    
    
    