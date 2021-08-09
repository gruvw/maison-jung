import printbetter as pb
import telegramBot
from server import adafruit, files


def main():
    pb.init()
    files.main()
    # adafruit.main()
    telegramBot.main()


# TODO long term:
# - Typing
# - Scheduler
# - Flask server (site)
