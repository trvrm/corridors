import numpy as np
from tqdm import tqdm
from .board import Board

from . import bots


def playGame(redBot, blueBot):

    board = Board()
    while not board.gameOver():
        bot = blueBot if board.turn == "blue" else redBot
        command = bot(board)
        board(*command)
    return board.winner()


def playGames(bot1, bot2, rounds=10):
    """
        Make it fair by playing both sides
    """

    winners12 = [playGame(bot1, bot2) for i in range(int(rounds / 2))]

    winners21 = [playGame(bot2, bot1) for i in range(int(rounds / 2))]

    return {
        "bot1": winners12.count("red") + winners21.count("blue"),
        "bot2": winners21.count("red") + winners12.count("blue"),
    }


# upgrade as we go!
baseline_bot = bots.StepsBot2()


def strength(bot):
    """
        Compute the strength of a bot by playing it against successively stronger bots
        and finding where the win/loss ration drops below 1.
        
        Returns a number between 0 and 1
    """

    def compare(bot, ratio):
        "Play 2 games against a bot at strength `i`"
        return (
            playGames(
                bot,
                bots.CombinedBot(
                    bots.RandomBot(),
                    baseline_bot,  # Ideally this would be our best available bot
                    ratio,
                ),
                rounds=2,
            )["bot1"]
            - 1
        )

    outcomes = []

    with tqdm(total=100) as pbar:
        for ratio in np.linspace(0, 1, 100):
            outcome = compare(bot, ratio)
            outcomes.append(outcome)
            pbar.update()

    outcomes = np.array(outcomes)

    return (((outcomes + 1) / 2).sum()) / 100


if __name__ == "__main__":

    # bot=bots.RandomBot()
    # print(f"Bot is {bot}")
    # print("Strength is {}".format(strength(bot)))
    #
    # bot = bots.StepsBot()
    # print(f"Bot is {bot}")
    # print("Strength is {}".format(strength(bot)))

    # bot = bots.StepsBot2()
    # print(f"Bot is {bot}")
    # print("Strength is {}".format(strength(bot)))

    bot = bots.StepsBot3()
    print(f"Bot is {bot}")
    print("Strength is {}".format(strength(bot)))

    # bot=bots.AlphaBetaBot(bots.StepsBot2())
    # print(f"Bot is {bot}")
    # print("Strength is {}".format(strength(bot)))

    #
    # print(
    #     playGames(
    #         bots.AlphaBetaBot(bots.StepsBot2()),
    #         bots.StepsBot2(),
    #         rounds=2
    #     )
    # )
