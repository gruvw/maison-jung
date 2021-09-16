import threading
import printbetter as pb
from Adafruit_IO import Client, MQTTClient

from . import actions
from ..utils import load_yaml, paths


config = load_yaml(paths['config'])

username = config['adafruit']['credentials']['username']
api_key = config['adafruit']['credentials']['key']

feeds_actions = {
    "lampes": actions.lampes,
    "stores": actions.stores,
    "arrosage": actions.arrosage
}


def connected(client):
    """The on-connect callback for MQTT with adafruit."""
    # Subscribes to each feeds
    for feed_id in config['adafruit']['feeds']['ids']:
        client.subscribe(feed_id)
    pb.info(f"<- [server] Connected to adafruit, subscribed to feeds: {', '.join([feed_id for feed_id in config['adafruit']['feeds']['ids']])}")


def message(client, feed_id, payload):
    """The on-message callback for MQTT with adafruit."""
    feeds_actions[config['adafruit']['feeds']['ids'][feed_id]](payload, "adafruit")


def main():
    """Adafruit initialisation and main loop."""
    if config['local']:  # do not send requests to adafruit or MQTT when on local PC
        return

    client = Client(username, api_key)  # basic client
    mqtt_client = MQTTClient(username, api_key)  # mqtt client

    # Reset feeds
    for feed_id, feed_name in config['adafruit']['feeds']['ids'].items():
        client.send(feed_id, config['adafruit']['feeds']['defaults'][feed_name])
    pb.info("-> [server] Adafruit feeds reset")

    # MQTT setup
    mqtt_client.on_connect = connected
    mqtt_client.on_message = message
    mqtt_client.connect()
    mqtt_client.loop_blocking()


def start():
    """Starts adafruit thread."""
    global thread
    pb.info("-> [server] Starting adafruit thread")
    thread = threading.Thread(target=main)
    thread.start()
