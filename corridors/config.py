import logging
import sys

def configureLogging():
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(threadName)22s %(name)18s: %(message)s',
        stream=sys.stdout,
    )