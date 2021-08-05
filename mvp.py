import yaml
from functools import wraps
import telegram
from telegram.ext import Updater


def restricted(func):
    """ Restricts handler usage to authorized users (present in config). """
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in config['telegram']['users'].values():
            print("Unauthorized access denied for {}.".format(user_id))
            return
        return func(update, context, *args, **kwargs)
    return wrapped

def getNewUsers():
    bot = telegram.Bot(token=config['telegram']['bot']['token'])
    updates = bot.get_updates()
    if updates:
        for update in updates:
            print(f"{update['message']['chat']['first_name']}: {update['message']['chat']['id']}")
    else:
        print("No new user, please send a message to the bot.")


def main():
    # Telegram bot
    # getNewUsers()
    updater = Updater(token=config['telegram']['bot']['token'])
    dispatcher = updater.dispatcher


# Load config file
with open("mvp.yml", 'r') as stream:
    config = yaml.safe_load(stream)

if __name__ == "__main__":
    main()
