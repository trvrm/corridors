import functools
import aiohttp
import pathlib
import logging
import asyncio
from aiohttp import web
import json
import sys
import uuid
import names
from .import config
from . import utilities
from . import game
PROJECT_ROOT= pathlib.Path(__file__).resolve().parent


'''
Workflow:

When you open the page, you get assigned a uid.

You see a LIST OF GAMES

You can START a game or ENTER a game.

A GAME has zero, one, or two players assigned to it.
You can join a game that has zero or one players assigned to it.

The backend tracks this stuff on the ws object.

The STATE object handles:
    a list of sockets
    a list of games
'''

class User:
    '''
        No serialization, recreated on each refresh for now.
    '''
    def __init__(self):
        self.uuid=uuid.uuid4()
        self.name=names.get_first_name()
        self.game=None
        
    def __str__(self):
        return self.name
    def __repr__(self):
        return f"User ({self.name}:{self.uuid})"

    def __json__(self):
        return {
            'name':self.name,
            'uuid':self.uuid
        }
        
class SharedState:
    def __init__(self):
        self.sockets=[]
        self.games=[]
        
    def flush(self):
        self.sockets=[
            s for s in self.sockets
            if not s.closed
        ]
        
    def game_list(self):
        return [
            {
                'uuid':game.uuid,
                'players':game.players,
                'turn':game.board.turn
            }
            for game in self.games
        ]
    def game_by_uuid(self,uuid):
        l=[g for g in self.games if g.uuid==uuid]
        if l:
            return l[0]
            

    
    
shared = SharedState()
message_handlers={}

def handle(name):
    def wrapper(func):
        message_handlers[name]=func
        return func
    return wrapper
    

@handle('new_game')
async def handle_new_game(ws):
    user=ws.user
    user.game=game.Game(player=user)
    
    shared.games.append(user.game)
    await ractive_set(ws,'user.game',user.game)
    await broadcast_game_list()

async def broadcast_game_list():
    await broadcast_set('games',shared.game_list())
    
@handle('join_game')
async def handle_join_game(ws,uuid):
    user=ws.user
    
    game=shared.game_by_uuid(uuid)
    if not game:
        await notify(ws,f"No such game: {uuid}","danger")
        logging.info(shared.games)
    elif (game.players['red'] is user) or (game.players['blue'] is user):
        await notify(ws,"Already in this game","danger")
    else:
        game.players['blue']=user
        user.game=game
        logging.info(shared.game_list())
        await ractive_set(ws,'user.game',user.game)
    await broadcast_game_list()
        
@handle('game.command')
async def handle_game_command(ws,command_text):
    logging.info(command_text)
    
    command=command_text.split()
    
    
    user=ws.user
    if user.game:
        try:
            if command[0] in ('hwall','vwall'):
                location = tuple([int(x) for x in command[1:]])
                assert len(location)==2
                command = [command[0],location]
                
            
            logging.info(command)
            user.game.board(*command)
            await ractive_set(ws,'user.game',user.game)
            
            # should also send to other user here!
            
            
        except Exception as e:
            await notify(ws,str(e),'danger')
            logging.exception(e)
    
async def broadcast_push(keypath,value):
    shared.flush()
    for socket in shared.sockets:
        try:
            await ractive_push(socket,keypath,value)
        except Exception as e:
            logging.error(e)
            
async def broadcast_set(keypath,value):
    shared.flush()
    for socket in shared.sockets:
        try:
            await ractive_set(socket,keypath,value)
        except Exception as e:
            logging.error(e)
            
async def ractive_set(ws,keypath,value):
    await ws.send_json(['set',keypath,value],dumps=utilities.dumps)
    
async def ractive_push(ws,keypath,value):
    await ws.send_json(['push',keypath,value],dumps=utilities.dumps)

async def index(_):
    text = (PROJECT_ROOT / 'index.html').read_text()
    return web.Response(text=text,content_type='text/html')
  
async def notify(ws,text,level='info'):
    await ractive_push(
        ws,
        'notifications',
        {'text':text,'level':level}
    )
async def process_message(ws,msg):
    stuff = json.loads(msg.data)
    logging.info(stuff)
    name=stuff[0]
    args=stuff[1:]
    
    func = message_handlers.get(name)
    
    
    if func:
        await func(ws, *args)
    else:
        await notify(ws,f'no such function: {name}','danger')
    
    
async def websocket_handler(request):
    try:
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        shared.sockets.append(ws)
        
        await ractive_set(ws,'test',"TEST MESsAGE")
        await notify(ws,"Hello")
        
        user=User()
        ws.user=user
        await ractive_set(ws,'user',user)
        await ractive_set(ws,'games',shared.game_list())
        
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                await process_message(ws,msg)
            elif msg.type == aiohttp.WSMsgType.ERROR:
                logging.warning('ws connection closed with exception {}'.format(ws.exception()))

        logging.info('websocket connection closed')

        return ws
    except asyncio.CancelledError as e:
        logging.warning('cancelled')
    except Exception as e:
        logging.exception(e)
        raise

    
    
app = web.Application()
app.router.add_get('/', index)
app.router.add_static('/public/',path=PROJECT_ROOT / 'public',name='public')
app.router.add_get('/ws/app/', websocket_handler)

if __name__=="__main__":
    config.configureLogging()
    logging.info("Let's go")
    web.run_app(app, host='0.0.0.0',port=8080)