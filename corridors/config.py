import logging
import sys


def configureLogging():
    # 
    # logging.basicConfig(
    #     level=logging.DEBUG,
    #     format="%(asctime)s %(name)8s: %(message)s",
    #     stream=sys.stdout,
    # )


    logging.basicConfig(
        stream=sys.stdout,
        level=logging.DEBUG,
        style='{',
        format='{asctime}\t{levelname}\t{filename:20} {lineno}: {message}',
    )
