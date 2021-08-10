from Adafruit_IO import Client, MQTTClient
from server import pb  # import printbetter from __init__.py
import server.actions
from server.utils import loadYaml


config = loadYaml("config")

# Adafruit clients
client = Client(config['adafruit']['credentials']['username'], config['adafruit']['credentials']['apiKey'])  # basic client
clientMQTT = MQTTClient(config['adafruit']['credentials']['username'], config['adafruit']['credentials']['apiKey'])  # mqtt client

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
    pb.info(f"<- [server] Connected to adafruit, subscribed to feeds: {', '.join([feedId for feedId in config['adafruit']['feeds']['ids']])}.")


def message(client, feed_id, payload):
    """The on-message function for MQTT with adafruit."""
    feedsActions[config['adafruit']['feeds']['ids'][feed_id]](payload, "adafruit")


def main():
    # Reset feeds
    if config['local']:  # do not send requests to adafruit or MQTT when on local PC
        return
    for feedName, default in config['adafruit']['feeds']['defaults'].items():
        feedIds = {v:k for k, v in config['adafruit']['feeds']['ids'].items()}
        client.send(feedIds[feedName], default)
    pb.info("-> [server] Adafruit feeds reset.")

    # MQTT setup
    clientMQTT.on_connect = connected
    clientMQTT.on_message = message
    clientMQTT.loop_background()
