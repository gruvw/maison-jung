import os
import printbetter as pb
import requests

from . import files
from .. import telegram_bot
from ..utils import bool_to_icon, load_yaml, paths


config = load_yaml(paths['config'])

max_retry = config['max_retry']  # nb of retries for wemos requests


def lampes(data, source, notify=True):
    """Takes actions (lampes) based on provided data. Returns if successful."""
    pb.info(f"<- [server] {source} | Lampes changed: {data}")  # data example: XXAXXXAXX
    from_scheduler = source == "scheduler"
    state = list(files.get_state("lampes"))
    successes = []
    for i, (lampe_name, wemos_ip) in enumerate(config['wemos']['lampes'].items()):
        if i+1 > len(data):  # not enough data for every wemos
            break
        action = data[i]  # A, Z
        if action == "X":
            continue
        lampe_action = "on" if action == "A" else "off"
        url = f"http://{wemos_ip}/Port0/{lampe_action}"
        success = sendWemos(url)
        successes.append(success)
        if success:  # request went well
            state[i] = action
            if notify:
                telegram_bot.actions.notify_users(f"{bool_to_icon(from_scheduler, 'clock')}👍 Lampes: _{lampe_name}_ -> _{lampe_action}_{f' (from {source})' if not from_scheduler else ''}", "lampes", f"{'scheduler' if from_scheduler else 'success'}")
        else:  # cannot join wemos
            state[i] = "P"
            if notify:
                telegram_bot.actions.notify_users(f"{bool_to_icon(from_scheduler, 'clock')}⚠️ Lampes: _{lampe_name}_ -> _{lampe_action}_{f' (from {source})' if not from_scheduler else ''}", "lampes", f"{'scheduler' if from_scheduler else 'errors'}")
    files.set_state("lampes", "".join(state))
    return all(successes)  # every requests went well


def stores(data, source, notify=True):
    """Takes actions (stores) based on provided data. Returns if successful."""
    pb.info(f"<- [server] {source} | Stores changed: {data}")  # data example: 3A0ZXX
    from_scheduler = source == "scheduler"
    stores_actions = {"A": "open", "Z": "close", "C": "clac", "I": "incli", "S": "stop"}
    successes = []
    for i, (store_name, wemos_ip) in enumerate(config['wemos']['stores'].items()):
        if i+1 > len(data):  # not enough data for every wemos
            break
        data_part = data[2*i:2*(i+1)]  # pairs of two chars (3A 0Z XX)
        action = data_part[1]  # A, Z, C, I, S
        if action == "X":
            continue
        store_nb = int(data_part[0])
        store_action = stores_actions[action]
        url_select = f"http://{wemos_ip}/{store_nb}"  # change selected store first
        url_action = f"http://{wemos_ip}/{store_action}"  # execute action after
        success = sendWemos(url_select) and sendWemos(url_action)  # sends both requests (first fails -> do not make second)
        successes.append(success)
        if success:  # request went well
            if notify:
                telegram_bot.actions.notify_users(f"{bool_to_icon(from_scheduler, 'clock')}👍 Stores: _{store_name} {'tous' if store_nb == 0 else store_nb}_ -> _{store_action}_{f' (from {source})' if not from_scheduler else ''}", "stores", f"{'scheduler' if from_scheduler else 'success'}")
        else:  # cannot join wemos
            if notify:
                telegram_bot.actions.notify_users(f"{bool_to_icon(from_scheduler, 'clock')}⚠️ Stores: _{store_name} {'tous' if store_nb == 0 else store_nb}_ -> _{store_action}_{f' (from {source})' if not from_scheduler else ''}", "stores", f"{'scheduler' if from_scheduler else 'errors'}")
    return all(successes)  # every requests went well


def arrosage(data, source, notify=True):
    """Takes action (arrosage) based on provided data. Returns if successful."""
    pb.info(f"<- [server] {source} | Arrosage changed: {data}")  # data example: 04A
    from_scheduler = source == "scheduler"
    # Only one vanne at a time
    action = data[2]  # A, Z
    vanne = int(data[:2])
    vanne_action = "on" if action == "A" else "off"
    wemos_ip = config['wemos']['arrosage']['armoire']
    url = f"http://{wemos_ip}/{vanne}/{vanne_action}"
    success = sendWemos(url)
    if success:  # request went well
        new_state = [data[2] if i+1 == int(data[:2]) else "Z" for i in range(48)]
        if notify:
            telegram_bot.actions.notify_users(f"{bool_to_icon(from_scheduler, 'clock')}👍 Arrosage: _vanne {vanne}_ -> _{vanne_action}_{f' (from {source})' if not from_scheduler else ''}", "arrosage", f"{'scheduler' if from_scheduler else 'success'}")
    else:  # cannot join wemos
        new_state = list("P"*48)
        if notify:
            telegram_bot.actions.notify_users(f"{bool_to_icon(from_scheduler, 'clock')}⚠️ Arrosage: _vanne {vanne}_ -> _{vanne_action}_{f' (from {source})' if not from_scheduler else ''}", "arrosage", f"{'scheduler' if from_scheduler else 'errors'}")
    files.set_state("arrosage", "".join(new_state))
    return success


def sendWemos(url, retry=0):
    """Get request to wemos with provided url. Returns if successful."""
    if retry > max_retry:
        pb.err(f"-> [server] Cannot send {url} to wemos!")
        return False
    elif retry > 0:
        pb.warn(f"-> [server] retry:{retry} | Sending wemos: {url}")
    else:
        pb.info(f"-> [server] Sending wemos: {url}")
    try:
        # Request
        if not config['local']:
            requests.get(url, headers={"Connection": "close"}, timeout=5)
        else:
            pb.info(f"[server] Simulated request locally ([GET] {url})")
        return True
    except Exception:
        return sendWemos(url, retry=retry+1)
