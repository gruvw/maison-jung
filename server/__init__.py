import printbetter as pb
import telegramBot
import scheduler
from server import adafruit, actions, files


def resetWemos():
    """Exectues actions sending wemos default values based on text files data."""
    # Lampes
    actions.lampes(files.getState("lampes"), "initialisation", notify=False)
    # Arrosage
    for i, action in enumerate(files.getState("arrosage")):
        vanneNb = str(i+1) if i+1 >= 10 else "0" + str(i+1)
        success = actions.arrosage(vanneNb + action, "initialisation", notify=False)
        if not success:  # if cannot communicate with wemos for vanne n, do not try to send for the other vannes
            break


def main():
    pb.init()
    pb.info("--- Initialisation ---")
    files.main()  # before resetWemos
    resetWemos()
    telegramBot.main()
    scheduler.main()
    adafruit.main()
    pb.info("--- Program ready ---")


# TODO long term:
# - Typing
# - Packaging
# - Unified database
# - Flask server (site)