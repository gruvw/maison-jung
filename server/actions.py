from server import pb # import printbetter from __init__.py
from server import files
from server.utils import loadYaml
import telegramBot.utils


config = loadYaml("config")

maxRetry = 2  # nb of retries for wemos requests


def lampes(data, source):
    """Takes correct actions (lampes) base on provided data. Returns if successful."""
    pb.info(f"<- {source} | Lampes changed: {data}")
    state = data.replace("X", "")
    lampeIndex = data.index(state)
    lampeName = list(config['wemos']['lampes'].keys())[lampeIndex]
    lampeState = 'on' if state == 'A' else 'off'
    wemosIp = list(config['wemos']['lampes'].values())[lampeIndex]
    url = f"http://{wemosIp}/Port0/{lampeState}"
    success = sendWemos(url)
    oldState = files.getState("lampes")
    if success:  # request went well
        state = [val if data[i] == "X" else data[i] for i, val in enumerate(oldState)]
        telegramBot.utils.notifyUsers(f"👍 Lampes: _{lampeName}_ -> _{lampeState}_ (from {source})", "lampes", "success")
    else:  # cannot join wemos
        state = [val if data[i] == "X" else "P" for i, val in enumerate(oldState)]
        telegramBot.utils.notifyUsers(f"⚠️ Lampes: _{lampeName}_ -> _{lampeState}_ (from {source})", "lampes", "errors")
    files.setState("lampes", "".join(state))
    return success


def stores(data, source):
    pb.info(f"<- {source} | Stores changed: {data}")


def arrosage(data, source):
    pb.info(f"<- {source} | Arrosage changed: {data}")
    state = [data[2] if i+1 == int(data[:2]) else "Z" for i in range(48)]
    files.setState("arrosage", "".join(state))


def sendWemos(url, retry=0):
    """Get request wemos with provided url. Returns if successful."""
    if retry > maxRetry:
        pb.err(f"-> Cannot send {url} to wemos!")
        return False
    elif retry > 0:
        pb.warn(f"-> retry:{retry} | Sending wemos: {url}")
    else:
        pb.info(f"-> Sending wemos: {url}")
    try:
        # request
        return True
    except Exception:
        return sendWemos(url, retry=retry+1)
