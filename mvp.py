import yaml
from functools import wraps
import telegram
from telegram import ChatAction, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler


############
# Telegram #
############

# Decorators and utilities

def restricted(func):
    """Restricts handler usage to authorized users (present in config)."""
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        userId = update.effective_user.id
        authorizedUsersId = [config['telegram']['users'][user]['id']
                             for user in config['telegram']['users']]
        if userId not in authorizedUsersId:
            print(f"Unauthorized access denied for {userId}.")
            return
        return func(update, context, *args, **kwargs)
    return wrapped


def sendAction(action):
    """Sends action while processing func command."""
    def decorator(func):
        @wraps(func)
        def command_func(update, context, *args, **kwargs):
            context.bot.send_chat_action(
                chat_id=update.effective_message.chat_id, action=action)
            return func(update, context,  *args, **kwargs)
        return command_func
    return decorator


def getNewUsers():
    """ Prints new telegram bot users and chat ids. """
    bot = telegram.Bot(token=config['telegram']['bot']['token'])
    updates = bot.get_updates()
    if updates:
        for update in updates:
            print(f"{update['message']['chat']['first_name']}: {update['message']['chat']['id']}")
    else:
        print("No new user, please send a message to the bot.")


def build_menu(buttons, n_cols):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    return menu

# Handlers


@restricted
# @sendAction(telegram.ChatAction.TYPING)
def start(update, context):
    context.bot.send_message(update.effective_chat.id,
                             "Bienvenu dans la famille JUNG!")


@restricted
def menu(update, context):
    replyMarkup = InlineKeyboardMarkup(build_menu(menus["main"]["buttons"], n_cols=2))
    context.bot.send_message(update.effective_chat.id, menus["main"]["text"], reply_markup=replyMarkup)


@restricted
def callback(update, context):
    query = update.callback_query
    data = query.data
    if data == "home":
        text = menus["main"]["text"]
        menu = menus["main"]["buttons"]
    else:
        text = menus[data]["text"]
        menu = [*menus[data]["buttons"], InlineKeyboardButton("< Home", callback_data="home")]
    replyMarkup = InlineKeyboardMarkup(build_menu(menu, n_cols=2))
    query.message.edit_text(text, reply_markup=replyMarkup)
    query.answer()


########
# Main #
########

def main():
    # getNewUsers()
    updater.start_polling(drop_pending_updates=True)


# Load config file
with open("config.yml", 'r') as stream:
    config = yaml.safe_load(stream)

# Telegram bot initialization
updater = Updater(token=config['telegram']['bot']['token'])
dispatcher = updater.dispatcher
handlersList = {
    "commands": [start, menu],
    "callback": [callback]
}
for func, handlers in handlersList.items():
    for handler in handlers:
        if func == "commands":
            newHandler = CommandHandler(handler.__name__, handler)
        elif func == "callback":
            newHandler = CallbackQueryHandler(handler)
        dispatcher.add_handler(newHandler)
menus = {
    "main": {
        "text": "Choisir le domaine:",
        "buttons": [
            InlineKeyboardButton("Lampes", callback_data="lampesSelect"),
            InlineKeyboardButton("Stores", callback_data="storesSelect"),
            InlineKeyboardButton("Arrosage", callback_data="arrosage"),
            InlineKeyboardButton("Paramètres", callback_data="parametersSelect")
        ]
    },
    "lampesSelect": {
        "text": "Choisir la lampe:",
        "buttons": [
            InlineKeyboardButton(name.title(), callback_data="lampesAction")
            for name in ["Chargeur", "Commode", "Bureau", "Canapé", "Ficus"]
        ]
    },
    "storesSelect": {
        "text": "Choisir le store:",
        "buttons": [
            InlineKeyboardButton(name.title(), callback_data="storesAction")
            for name in ["Tous", "1", "2", "3", "4", "5"]
        ]
    },
    "parametersSelect": {
        "text": "Choisir le paramètre:",
        "buttons": [
            InlineKeyboardButton(name.title(), callback_data="parametersAction")
            for name in config['telegram']['bot']['settings']
        ]
    },
    "lampesAction": {
        "text": "Que faire avec la lampe:",
        "buttons": [
            InlineKeyboardButton("Allumer", callback_data="lampesOn"),
            InlineKeyboardButton("Éteindre", callback_data="lampesOff")
        ]
    },
    "storesAction": {
        "text": "Que faire avec le store:",
        "buttons": [
            InlineKeyboardButton("Monter", callback_data="storesUp"),
            InlineKeyboardButton("Descendre", callback_data="storesDown"),
            InlineKeyboardButton("Clac-clac", callback_data="storesClac"),
            InlineKeyboardButton("Stop", callback_data="storesStop")
        ]
    }
}

if __name__ == "__main__":
    main()
