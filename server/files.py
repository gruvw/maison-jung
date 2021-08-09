from server import pb # import printbetter from __init__.py
from server.utils import loadYaml


config = loadYaml("config")


def resetFiles():
    for name, path in config['files']['state']['paths'].items():
        with open(path, "w") as file:
            file.write(config['files']['state']['defaults'][name])
    pb.info("Text files reset.")


def setState(name, state):
    with open(config['files']['state']['paths'][name], "w") as file:
        file.write(state)
    pb.info(f"-> Wrote state {state} to text file {name}.")


def getState(name):
    with open(config['files']['state']['paths'][name], "r") as file:
        return file.read()


def main():
    resetFiles()
