# Maison Jung

This is the python package that runs on the Raspberry Pi managing the custom made IOT in my house.

## Usage

The package exposes a CLI: `maison-jung --help`

It requires multiple files to be inside a working directory in order to run properly:

- _config.yml_: where are stored API keys (for the [telegram bot](https://github.com/python-telegram-bot/python-telegram-bot) and [Adafruit IO](https://io.adafruit.com/Dedelejardinier/dashboards)), all the [wemos](https://www.wemos.cc/) ips, ...
- _options.yml_: used to build the interactive inline keyboard menu on telegram
- _schedules.yml_: defines the scheduled tasks
- _database.json_: [TinyDB](https://github.com/msiemens/tinydb) database

## To Do

- [ ] Type hinting
- [ ] Text files data in database table (ready for drop)
- [ ] Flask server (website)
