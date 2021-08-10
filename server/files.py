from server import pb # import printbetter from __init__.py
from server.utils import loadYaml


config = loadYaml("config")


def resetFiles():
    """Resets text files to default values found in config."""
    for name, path in config['files']['state']['paths'].items():
        with open(path, "w") as file:
            file.write(config['files']['state']['defaults'][name])
    pb.info("-> [server] Text files reset.")


def setState(name, state):
    """Sets new text file content."""
    with open(config['files']['state']['paths'][name], "w") as file:
        file.write(state)
    pb.info(f"-> [server] Wrote state {state} to text file {name}.")


def getState(name):
    """Return text file content."""
    with open(config['files']['state']['paths'][name], "r") as file:
        return file.read()


def main():
    resetFiles()
