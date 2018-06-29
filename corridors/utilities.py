import functools
import uuid
import json
def default_encoder(thing):
    if isinstance(thing,uuid.UUID):
        return str(thing)
    if hasattr(thing,'__json__'):
        return thing.__json__()
    raise TypeError(repr(thing) + ' is not JSON serializable')

dumps = functools.partial(json.dumps,indent=0, sort_keys=True,ensure_ascii=False, default=default_encoder)

