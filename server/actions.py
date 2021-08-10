import requests
from server import pb  # import printbetter from __init__.py
from server import files
from server.utils import loadYaml
import telegramBot.utils


config = loadYaml("config")

maxRetry = 2  # nb of retries for wemos requests

# TODO from scheduler + emoji, si erreur en scheduler, group: errors or scheduler?
def lampes(data, source):
    """Takes actions (lampes) based on provided data. Returns if successful."""
    pb.info(f"<- {source} | Lampes changed: {data}")  # data example: XXAXXXXXX
    state = list(files.getState("lampes"))
    successes = []
    for i in range(len(data)):
        action = data[i]  # A, Z
        if action == "X":
            continue
        lampeName = list(config['wemos']['lampes'].keys())[i]
        lampeAction = 'on' if action == 'A' else 'off'
        wemosIp = list(config['wemos']['lampes'].values())[i]
        url = f"http://{wemosIp}/Port0/{lampeAction}"
        success = sendWemos(url)
        successes.append(success)
        if success:  # request went well
            state[i] = action
            telegramBot.utils.notifyUsers(f"👍 Lampes: _{lampeName}_ -> _{lampeAction}_ (from {source})", "lampes", "success")
        else:  # cannot join wemos
            state[i] = "P"
            telegramBot.utils.notifyUsers(f"⚠️ Lampes: _{lampeName}_ -> _{lampeAction}_ (from {source})", "lampes", "errors")
    files.setState("lampes", "".join(state))
    return all(successes)  # every requests went well


def stores(data, source):
    """Takes actions (stores) based on provided data. Returns if successful."""
    pb.info(f"<- {source} | Stores changed: {data}")  # data example: 3A0ZXX
    storesActions = {"A": "open", "Z": "close", "C": "clac", "I": "incli", "S": "stop"}
    successes = []
    for i in range(3):
        dataPart = data[2*i:2*(i+1)]  # pairs of two chars (3A 0Z XX)
        action = dataPart[1]  # A, Z, C, I, S
        if action == "X":
            continue
        storeNb = int(dataPart[0])
        storeName = list(config['wemos']['stores'].keys())[i]
        storeAction = storesActions[action]
        wemosIp = list(config['wemos']['stores'].values())[i]
        urlSelect = f"http://{wemosIp}/{storeNb}"  # change selected store first
        urlAction = f"http://{wemosIp}/{storeAction}"  # execute action after
        success = sendWemos(urlSelect) and sendWemos(urlAction)  # sends both requests
        successes.append(success)
        if success:  # request went well
            telegramBot.utils.notifyUsers(f"👍 Stores: _{storeName} {'tous' if storeNb == 0 else storeNb}_ -> _{storeAction}_ (from {source})", "stores", "success")
        else:  # cannot join wemos
            telegramBot.utils.notifyUsers(f"⚠️ Stores: _{storeName} {'tous' if storeNb == 0 else storeNb}_ -> _{storeAction}_ (from {source})", "stores", "errors")
    return all(successes)  # every requests went well


def arrosage(data, source):
    """Takes action (arrosage) based on provided data. Returns if successful."""
    pb.info(f"<- {source} | Arrosage changed: {data}")  # data example: 04A
    # Only one vanne at a time
    action = data[2]  # A, Z
    vanne = int(data[:2])
    vanneAction = 'on' if action == 'A' else 'off'
    wemosIp = config['wemos']['arrosage']['armoire']
    url = f"http://{wemosIp}/{vanne}/{vanneAction}"
    success = sendWemos(url)
    if success:  # request went well
        newState = [data[2] if i+1 == int(data[:2]) else "Z" for i in range(48)]
        telegramBot.utils.notifyUsers(f"👍 Arrosage: _vanne {vanne}_ -> _{vanneAction}_ (from {source})", "arrosage", "success")
    else:  # cannot join wemos
        newState = list("P"*48)
        telegramBot.utils.notifyUsers(f"⚠️ Arrosage: _vanne {vanne}_ -> _{vanneAction}_ (from {source})", "arrosage", "errors")
    files.setState("arrosage", "".join(newState))
    return success


def sendWemos(url, retry=0):
    """Get request to wemos with provided url. Returns if successful."""
    if retry > maxRetry:
        pb.err(f"-> Cannot send {url} to wemos!")
        return False
    elif retry > 0:
        pb.warn(f"-> retry:{retry} | Sending wemos: {url}")
    else:
        pb.info(f"-> Sending wemos: {url}")
    try:
        # request
        if not config['local']:
            requests.get(url, headers={'Connection': 'close'})
        return True
    except Exception:
        return sendWemos(url, retry=retry+1)
