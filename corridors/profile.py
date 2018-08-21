# unit tests
import corridors
from corridors import config
import corridors.board
import corridors.utilities
import corridors.bots
import corridors.movement
import datetime
import contextlib


@contextlib.contextmanager
def timed():
    start = datetime.datetime.now()
    try:
        yield
    finally:
        duration = datetime.datetime.now() - start
        print(duration)


def test_speed():
    with timed():
        board = corridors.board.Board()
        bot = corridors.bots.StepsBot2()
        movecount = 0
        while not board.gameOver():
            command = bot(board)

            board(*command)

            movecount += 1
        print("Winner: {}, movecount: {}".format(board.winner(), movecount))


def test_speed_2():

    with timed():
        b = corridors.board.Board()

        evalbot = corridors.bots.StepsBot2()
        # evalbot=corridors.bots.DumbBot()
        bot = corridors.bots.AlphaBetaBot(evalbot)

        move = bot(b)
        print(move)


def test_speed_ab():
    with timed():
        board = corridors.board.Board()
        bot = corridors.bots.AlphaBetaBot(corridors.bots.StepsBot3())
        movecount = 0
        while movecount < 10:
            command = bot(board)
            board(*command)
            movecount += 1
        print(" movecount: {}".format(movecount))


def test_speed_pybind_ab():
    print("test_speed_pybind_ab")
    from corridors import _corridors

    with timed():
        board = _corridors.Board()
        bot = _corridors.AlphaBetaBot()
        movecount = 0
        while movecount < 10:
            command = bot.call(board)
            board.apply(command)
            movecount += 1
        print(" movecount: {}".format(movecount))


def test_speed_pybind():
    print("test_speed_pybind")
    from corridors import _corridors

    with timed():
        board = _corridors.Board()
        bot = _corridors.StepsBot2()
        movecount = 0
        while not board.gameOver():
            command = bot.call(board)

            board.apply(command)

            movecount += 1
        print(" movecount: {}".format(movecount))


if __name__ == "__main__":
    config.configureLogging()
    test_speed_ab()
    test_speed_pybind_ab()
    # test_speed_2()
    # test_speed()
    # test_speed_pybind()
