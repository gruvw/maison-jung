import click
import os.path

from . import utils


def validate_directory(ctx, param, value):
    value = value if value.endswith("/") else value + "/"
    required_files = utils.paths.values()
    for file in required_files:
        if not os.path.isfile(value + file):
            raise click.BadParameter(f"The working directory must contain {file}.")
    return value


@click.command()
@click.argument("directory", type=click.Path(exists=True, writable=True), callback=validate_directory)
def run(directory):
    """
    Starts the maison-jung server.

    \b
    The working directory (DIRECTORY) should contain the following files:
      - config.yml: configuration file
      - options.yml: telegram menus options
      - schedules.yml: scheduled tasks
      - database.json: TinyDB database
    """
    for key in utils.paths:
        utils.paths[key] = directory + utils.paths[key]
    utils.paths['directory'] = directory

    from . import server
    server.main.start()


if __name__ == "__main__":
    run()
