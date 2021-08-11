import os
from Adafruit_IO import Client, MQTTClient
from server import pb  # import printbetter from __init__.py
import server.actions
from server.utils import loadYaml


config = loadYaml("config")

# Adafruit clients
username, apiKey = config['adafruit']['credentials']['username'], config['adafruit']['credentials']['apiKey']
client = Client(username, apiKey)  # basic client
clientMQTT = MQTTClient(username, apiKey)  # mqtt client

feedsActions = {
    "lampes": server.actions.lampes,
    "stores": server.actions.stores,
    "arrosage": server.actions.arrosage
}


def connected(client):
    """The connect function for MQTT with adafruit."""
    # Subscribes to each feeds
    for feedId in config['adafruit']['feeds']['ids']:
        client.subscribe(feedId)
    pb.info(f"<- [server] Connected to adafruit, subscribed to feeds: {', '.join([feedId for feedId in config['adafruit']['feeds']['ids']])}")


def message(client, feed_id, payload):
    """The on-message function for MQTT with adafruit."""
    feedsActions[config['adafruit']['feeds']['ids'][feed_id]](payload, "adafruit")


def main():
    # Reset feeds
    if os.environ["APP_SCOPE"] == "local":  # do not send requests to adafruit or MQTT when on local PC
        return
    for feedId, feedName in config['adafruit']['feeds']['ids'].items():
        client.send(feedId, config['adafruit']['feeds']['defaults'][feedName])
    pb.info("-> [server] Adafruit feeds reset")

    # MQTT setup
    clientMQTT.on_connect = connected
    clientMQTT.on_message = message
    clientMQTT.connect()
    clientMQTT.loop_background()
