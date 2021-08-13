import printbetter as pb

from . import adafruit, actions, files
from .. import scheduler, telegram_bot, utils


def reset_wemos():
    """Exectues actions sending wemos default values based on text files data."""
    # Lampes
    actions.lampes(files.get_state("lampes"), "initialisation", notify=False)
    # Arrosage
    for i, action in enumerate(files.get_state("arrosage")):
        vanne_nb = str(i+1) if i+1 >= 10 else "0" + str(i+1)
        success = actions.arrosage(vanne_nb + action, "initialisation", notify=False)
        if not success:  # if cannot communicate with wemos for vanne n, do not try to send for the other vannes
            break


def start():
    pb.init(logPath=utils.paths['directory']+"logs/%d-%m-%y_%H.%M.%S.log")
    pb.info("--- Initialisation ---")
    files.reset_files()  # before reset_wemos
    reset_wemos()
    telegram_bot.main.start()
    scheduler.main.start()
    adafruit.start()
    pb.info("--- Program ready ---")


# TODO long term:
# - Typing
# - Packaging
# - printbetter import
# - text files in DB (ready for drop)
# - Flask server (site)