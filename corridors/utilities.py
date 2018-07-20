import functools
import uuid
import json
import datetime
import contextlib
import logging

@contextlib.contextmanager
def timed():
    start=datetime.datetime.now()
    try:
        yield  
    finally:
        duration=datetime.datetime.now()-start
        logging.info(duration)
        
def default_encoder(thing):
    if isinstance(thing,uuid.UUID):
        return str(thing)
    if hasattr(thing,'__json__'):
        return thing.__json__()
    raise TypeError(repr(thing) + ' is not JSON serializable')

dumps = functools.partial(json.dumps,indent=0, sort_keys=True,ensure_ascii=False, default=default_encoder)

