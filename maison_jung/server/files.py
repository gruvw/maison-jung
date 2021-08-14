import printbetter as pb

from ..utils import load_yaml, paths


config = load_yaml(paths['config'])


def reset_files():
    """Resets text files to default values found in config."""
    for name, path in config['files']['state']['paths'].items():
        with open(paths['directory'] + path, "w+") as file:
            file.write(config['files']['state']['defaults'][name])
    pb.info("-> [server] Text files reset")


def set_state(name, state):
    """Sets new text file content."""
    with open(paths['directory'] + config['files']['state']['paths'][name], "w") as file:
        file.write(state)
    pb.info(f"-> [server] Wrote state {state} to text file {name}")


def get_state(name):
    """Returns text file content."""
    with open(paths['directory'] + config['files']['state']['paths'][name], "r") as file:
        return file.read()
