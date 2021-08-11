import os
import requests
from server import pb  # import printbetter from __init__.py
from server import files
from server.utils import boolToIcon, loadYaml
import telegramBot.utils


config = loadYaml("config")

maxRetry = 2  # nb of retries for wemos requests


def lampes(data, source, notify=True):
    """Takes actions (lampes) based on provided data. Returns if successful."""
    pb.info(f"<- [server] {source} | Lampes changed: {data}")  # data example: XXAXXXAXX
    fromScheduler = source == "scheduler"
    state = list(files.getState("lampes"))
    successes = []
    for i, (lampeName, wemosIp) in enumerate(config['wemos']['lampes'].items()):
        if i+1 > len(data):  # not enough data for every wemos
            break
        action = data[i]  # A, Z
        if action == "X":
            continue
        lampeAction = 'on' if action == 'A' else 'off'
        url = f"http://{wemosIp}/Port0/{lampeAction}"
        success = sendWemos(url)
        successes.append(success)
        if success:  # request went well
            state[i] = action
            if notify:
                telegramBot.utils.notifyUsers(f"{boolToIcon(fromScheduler, 'clock')}👍 Lampes: _{lampeName}_ -> _{lampeAction}_{f' (from {source})' if not fromScheduler else ''}", "lampes", f"{'scheduler' if fromScheduler else 'success'}")
        else:  # cannot join wemos
            state[i] = "P"
            if notify:
                telegramBot.utils.notifyUsers(f"{boolToIcon(fromScheduler, 'clock')}⚠️ Lampes: _{lampeName}_ -> _{lampeAction}_{f' (from {source})' if not fromScheduler else ''}", "lampes", f"{'scheduler' if fromScheduler else 'errors'}")
    files.setState("lampes", "".join(state))
    return all(successes)  # every requests went well


def stores(data, source, notify=True):
    """Takes actions (stores) based on provided data. Returns if successful."""
    pb.info(f"<- [server] {source} | Stores changed: {data}")  # data example: 3A0ZXX
    fromScheduler = source == "scheduler"
    storesActions = {"A": "open", "Z": "close", "C": "clac", "I": "incli", "S": "stop"}
    successes = []
    for i, (storeName, wemosIp) in enumerate(config['wemos']['stores'].items()):
        if i+1 > len(data):  # not enough data for every wemos
            break
        dataPart = data[2*i:2*(i+1)]  # pairs of two chars (3A 0Z XX)
        action = dataPart[1]  # A, Z, C, I, S
        if action == "X":
            continue
        storeNb = int(dataPart[0])
        storeAction = storesActions[action]
        urlSelect = f"http://{wemosIp}/{storeNb}"  # change selected store first
        urlAction = f"http://{wemosIp}/{storeAction}"  # execute action after
        success = sendWemos(urlSelect) and sendWemos(urlAction)  # sends both requests
        successes.append(success)
        if success:  # request went well
            if notify:
                telegramBot.utils.notifyUsers(f"{boolToIcon(fromScheduler, 'clock')}👍 Stores: _{storeName} {'tous' if storeNb == 0 else storeNb}_ -> _{storeAction}_{f' (from {source})' if not fromScheduler else ''}", "stores", f"{'scheduler' if fromScheduler else 'success'}")
        else:  # cannot join wemos
            if notify:
                telegramBot.utils.notifyUsers(f"{boolToIcon(fromScheduler, 'clock')}⚠️ Stores: _{storeName} {'tous' if storeNb == 0 else storeNb}_ -> _{storeAction}_{f' (from {source})' if not fromScheduler else ''}", "stores", f"{'scheduler' if fromScheduler else 'errors'}")
    return all(successes)  # every requests went well


def arrosage(data, source, notify=True):
    """Takes action (arrosage) based on provided data. Returns if successful."""
    pb.info(f"<- [server] {source} | Arrosage changed: {data}")  # data example: 04A
    fromScheduler = source == "scheduler"
    # Only one vanne at a time
    action = data[2]  # A, Z
    vanne = int(data[:2])
    vanneAction = 'on' if action == 'A' else 'off'
    wemosIp = config['wemos']['arrosage']['armoire']
    url = f"http://{wemosIp}/{vanne}/{vanneAction}"
    success = sendWemos(url)
    if success:  # request went well
        newState = [data[2] if i+1 == int(data[:2]) else "Z" for i in range(48)]
        if notify:
            telegramBot.utils.notifyUsers(f"{boolToIcon(fromScheduler, 'clock')}👍 Arrosage: _vanne {vanne}_ -> _{vanneAction}_{f' (from {source})' if not fromScheduler else ''}", "arrosage", f"{'scheduler' if fromScheduler else 'success'}")
    else:  # cannot join wemos
        newState = list("P"*48)
        if notify:
            telegramBot.utils.notifyUsers(f"{boolToIcon(fromScheduler, 'clock')}⚠️ Arrosage: _vanne {vanne}_ -> _{vanneAction}_{f' (from {source})' if not fromScheduler else ''}", "arrosage", f"{'scheduler' if fromScheduler else 'errors'}")
    files.setState("arrosage", "".join(newState))
    return success


def sendWemos(url, retry=0):
    """Get request to wemos with provided url. Returns if successful."""
    if retry > maxRetry:
        pb.err(f"-> [server] Cannot send {url} to wemos!")
        return False
    elif retry > 0:
        pb.warn(f"-> [server] retry:{retry} | Sending wemos: {url}")
    else:
        pb.info(f"-> [server] Sending wemos: {url}")
    try:
        # request
        if not os.environ["APP_SCOPE"] == "local":
            requests.get(url, headers={'Connection': 'close'})
        else:
            pb.info(f"[server] Simulated request locally ([GET] {url})")
        return True
    except Exception:
        return sendWemos(url, retry=retry+1)
