import os
import printbetter as pb
from Adafruit_IO import Client, MQTTClient

from . import actions
from ..utils import load_yaml, paths


config = load_yaml(paths['config'])

# Adafruit clients
username, api_key = config['adafruit']['credentials']['username'], config['adafruit']['credentials']['key']
client = Client(username, api_key)  # basic client
mqtt_client = MQTTClient(username, api_key)  # mqtt client

feeds_actions = {
    "lampes": actions.lampes,
    "stores": actions.stores,
    "arrosage": actions.arrosage
}


def connected(client):
    """The connect function for MQTT with adafruit."""
    # Subscribes to each feeds
    for feed_id in config['adafruit']['feeds']['ids']:
        client.subscribe(feed_id)
    pb.info(f"<- [server] Connected to adafruit, subscribed to feeds: {', '.join([feed_id for feed_id in config['adafruit']['feeds']['ids']])}")


def message(client, feed_id, payload):
    """The on-message function for MQTT with adafruit."""
    feeds_actions[config['adafruit']['feeds']['ids'][feed_id]](payload, "adafruit")


def start():
    # Reset feeds
    if config['local']:  # do not send requests to adafruit or MQTT when on local PC
        return
    for feed_id, feed_name in config['adafruit']['feeds']['ids'].items():
        client.send(feed_id, config['adafruit']['feeds']['defaults'][feed_name])
    pb.info("-> [server] Adafruit feeds reset")

    # MQTT setup
    mqtt_client.on_connect = connected
    mqtt_client.on_message = message
    mqtt_client.connect()
    mqtt_client.loop_background()
