# Maison Jung

This is the repository where I host the server programs that runs on the Raspberry Pi managing the custom IOT in my house.

### Requirements

Install dependencies:

`python3 -m pip install printbetter schedule adafruit-io python-telegram-bot tinydb PyYAML suntime`


#### Notes

The following files are ignored by git for security & privacy reasons:

- `logs/*`
- `textFiles/*`
- `telegramBot/databases/*`
- `config.yml`
- `telegramBot/options.yml`
- `scheduler/schedules.yml`

#### YAML files format

##### `config.yml`:

```yaml
wemos:
  lampes:
    # name: wemosIp
    # ...
  stores:
    # name: wemosIp
    # ...
  arrosage:
    # name: wemosIp
    # ...
files:
  state:
    paths:
      # name: path.txt
      # ...
    defaults:
      # feedName: defaultValue
      # ...
location: [0, 0]  # latitude, longitude
telegram:
  bots:
    token:
      # name: apiToken
      # ...
  database:
    path:
      # name: path.json
      # ...
adafruit:
  credentials:
    username: # username
    apiKey: # apiKey
  feeds:
    ids:
      # feedId: feedName
      # ...
    defaults:
      # feedName: defaultValue
      # ...
```
