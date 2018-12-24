
import aiohttp
import pathlib
import logging
import asyncio
from aiohttp import web
import json


from . import config
from . import utilities

from . import bots
from . import cpp_bots
from .game import Game
from .user import User
from .board import locationFromDirection, hopTarget
from .state import SharedState

PROJECT_ROOT = pathlib.Path(__file__).resolve().parent


def new_user():
    n = 2 + len(shared.users)
    name = f"User {n}"
    return User(name)


shared = SharedState()
message_handlers = {}


def handle(name):
    def wrapper(func):
        message_handlers[name] = func
        return func

    return wrapper


@handle("new_game")
async def handle_new_game(ws, who):
    assert who in ("human", "bot")

    game = Game(red=ws.user)

    if "bot" == who:
        # game.players['blue']=bots.AlphaBetaBot(bots.StepsBot3())
        # game.players['blue']=bots.StepsBot2()
        # game.players['blue']=bots.AlphaBetaBot(bots.DumbBot())
        game.players["blue"] = cpp_bots.CPPAlphaBetaBot(max_depth=4)

    ws.game = game
    shared.games.append(game)

    await ractive_set(ws, "current_color", "red")
    await ractive_set(ws, "other_color", "blue")
    await ractive_set(ws, "current_game", game)
    await broadcast_game_list()


async def broadcast_game_list():
    await broadcast_set("games", shared.game_list())


@handle("join_game")
async def handle_join_game(ws, uuid):
    user = ws.user

    game = shared.game_by_uuid(uuid)
    if not game:
        await notify(ws, f"No such game: {uuid}", "danger")
        logging.info(shared.games)
    elif (game.players["red"] is user) or (game.players["blue"] is user):
        await notify(ws, "Already in this game", "danger")
    else:
        game.players["blue"] = user

        ws.game = game
        logging.info(shared.game_list())

        await ractive_set(ws, "current_color", "blue")
        await ractive_set(ws, "other_color", "red")
        await ractive_set(ws, "current_game", game)
    await broadcast_game_list()


def user_can_move(ws):
    game = ws.game
    if not game:
        return False
    user = ws.user
    if not user:
        return False
    assert game.board.turn in ("red", "blue")
    player = game.players[game.board.turn]
    if player != user:
        return False
    return True


@handle("game.select")
async def handle_game_select(ws, what):
    """
        User selected a piece or a wall to move/place
    """
    assert what in ("piece", "wall")
    assert user_can_move(ws), "User can't currently make a move on this board."

    game = ws.game

    if what == "wall":
        if game.selected == "hwall":
            game.selected = "vwall"
        else:
            game.selected = "hwall"
    else:
        if game.selected == "piece":
            game.selected = None
        else:
            game.selected = "piece"

    await ractive_set(ws, "current_game.selected", game.selected)

    # massive scope for optimization here!
    commands = list(game.board.allLegalCommands())
    # send available moves/wall
    if game.selected == "piece":
        commands = [c for c in commands if c[0] in ("hop", "move")]
        piece = game.board.currentPiece()
        location = piece.location

        locations = [
            locationFromDirection(location, c[1])
            if c[0] == "move"
            else hopTarget(location, c[1], c[2])
            for c in commands
        ]

    else:
        commands = [c for c in commands if c[0] == game.selected]  # hwall or vwall
        locations = [c[1] for c in commands if c[0] == game.selected]

    await ractive_set(ws, "current_game.locations", locations)
    await ractive_set(ws, "current_game.commands", commands)

    # If it's a piece we should set currently available moves?
    #


@handle("game.command")
async def handle_game_command(ws, command):

    if isinstance(command, str):
        command = command.split()
    else:
        assert isinstance(command, list)

    # logging.info(command)
    user = ws.user

    game = ws.game
    if not game:
        return

    # should check that game.user ==ws.user!

    assert game.board.turn in ("red", "blue")
    player = game.players[game.board.turn]
    assert player == user, "user/player mismatch"

    # ok so this user is playing on this board and can make a move.

    game.selected = None
    try:
        if command[0] in ("hwall", "vwall"):
            # location = tuple([int(x) for x in command[1:]])
            location = command[1]

            assert len(location) == 2
            # command = [command[0],location]

        logging.info(command)
        # really need a
        game.board(*command)

        await ractive_set(ws, "current_game", game)

        if isinstance(game.players["blue"], bots.BaseBot):
            if not game.board.gameOver():
                bot = game.players["blue"]
                # This should probably be run in a threadpool
                command = bot(game.board)
                logging.info("Bot suggests :{}".format(command))
                game.board(*command)
                await ractive_set(ws, "current_game", game)

        else:
            sockets = shared.sockets_for_game(game.uuid)
            for s in sockets:
                await ractive_set(s, "current_game", game)

    except Exception as e:
        await notify(ws, str(e), "danger")
        logging.exception(e)


async def broadcast_push(keypath, value):
    shared.flush()
    for socket in shared.sockets:
        try:
            await ractive_push(socket, keypath, value)
        except Exception as e:
            logging.error(e)


async def broadcast_set(keypath, value):
    shared.flush()
    for socket in shared.sockets:
        try:
            await ractive_set(socket, keypath, value)
        except Exception as e:
            logging.error(e)


async def ractive_set(ws, keypath, value):
    await ws.send_json(["set", keypath, value], dumps=utilities.dumps)


async def ractive_push(ws, keypath, value):
    await ws.send_json(["push", keypath, value], dumps=utilities.dumps)


async def index(_):
    text = (PROJECT_ROOT / "index.html").read_text()
    return web.Response(text=text, content_type="text/html")


async def notify(ws, text, level="info"):
    await ractive_push(ws, "notifications", {"text": text, "level": level})


async def process_message(ws, msg):
    stuff = json.loads(msg.data)
    logging.info(stuff)
    name = stuff[0]
    args = stuff[1:]

    func = message_handlers.get(name)

    if func:
        await func(ws, *args)
    else:
        await notify(ws, f"no such function: {name}", "danger")


async def websocket_handler(request):
    try:
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        shared.sockets.append(ws)

        ws.user = new_user()
        shared.users.append(ws.user)
        await ractive_set(ws, "user", ws.user)
        await ractive_set(ws, "games", shared.game_list())

        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                await process_message(ws, msg)
            elif msg.type == aiohttp.WSMsgType.ERROR:
                logging.warning(
                    "ws connection closed with exception {}".format(ws.exception())
                )

        logging.info("websocket connection closed")

        return ws
    except asyncio.CancelledError as e:
        logging.warning("cancelled")
    except Exception as e:
        logging.exception(e)
        raise


app = web.Application()
app.router.add_get("/", index)
app.router.add_static("/public/", path=PROJECT_ROOT / "public", name="public")
app.router.add_get("/ws/app/", websocket_handler)

if __name__ == "__main__":
    config.configureLogging()
    logging.info("Let's go")
    web.run_app(app, host="0.0.0.0", port=8080)
