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
        if not success:  # if cannot communicate with wemos for vanne n, do not try to request for the rest
            break


def start():
    pb.init(log_path=utils.paths['directory']+"logs/%d-%m-%y_%H.%M.%S.log")
    pb.info("--- Initialisation ---")
    files.reset_files()  # before reset_wemos
    reset_wemos()
    telegram_bot.main.start()
    adafruit.start()  # before scheduler
    scheduler.main.start()
    pb.info("--- Program ready ---")
