import yaml
from functools import wraps
import telegram
from telegram import ChatAction, InlineKeyboardButton, KeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, commandhandler


############
# Telegram #
############

# Load config file
with open("config.yml", 'r') as stream:
    config = yaml.safe_load(stream)

# Telegram bot initialization
updater = Updater(token=config['telegram']['bot']['token'])
dispatcher = updater.dispatcher

# Decorators and utilities

def commandHandler(func):
    """Registers a function as a command handler."""
    handler = CommandHandler(func.__name__, func)
    dispatcher.add_handler(handler)
    return func

def callbackHandler(func):
    """Registers a function as a command handler."""
    handler = CallbackQueryHandler(func)
    dispatcher.add_handler(handler)
    return func

def restricted(func):
    """Restricts handler usage to authorized users (present in config)."""
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        userId = update.effective_user.id
        authorizedUsersId = [config['telegram']['users'][user]['chatId'] for user in config['telegram']['users']]
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

@commandHandler
@restricted
# @sendAction(telegram.ChatAction.TYPING)
def start(update, context):
    context.bot.send_message(update.effective_chat.id, "Bienvenu dans la famille JUNG!")

@commandHandler
@restricted
def menu(update, context):
    replyMarkup = InlineKeyboardMarkup(build_menu(menus["main"]["buttons"], n_cols=2))
    context.bot.send_message(update.effective_chat.id, menus["main"]["message"], reply_markup=replyMarkup)

@callbackHandler
@restricted
def callback(update, context):
    query = update.callback_query
    data = query.data
    chatId = update.effective_chat.id
    query.answer()
    selection[chatId].append(data)
    if data == "home":
        scene = menus["main"]
        selection[chatId].clear()
    if len(selection[chatId]) == 1:
        scene = menus[data+"Select"]
    elif len(selection[chatId]) == 2:
        scene = menus[selection[chatId][0]+"Action"]
    elif len(selection[chatId]) == 3:
        scene = menus["main"]
        # ACTION
        context.bot.send_message(update.effective_chat.id, selection[chatId])
        selection[chatId].clear()
    buttons = scene["buttons"]
    if selection[chatId]:
        buttons = [*buttons, InlineKeyboardButton("< Home", callback_data="home")]
    replyMarkup = InlineKeyboardMarkup(build_menu(buttons, n_cols=2))
    query.message.edit_text(scene["message"], reply_markup=replyMarkup)


########
# Main #
########

def main():
    # getNewUsers()
    updater.start_polling(drop_pending_updates=True)
    updater.idle()


menus = {
    "main": {
        "message": "Choisir le domaine:",
        "buttons": [
            InlineKeyboardButton("Lampes", callback_data="lampes"),
            InlineKeyboardButton("Stores", callback_data="stores"),
            InlineKeyboardButton("Arrosage", callback_data="arrosage"),
            InlineKeyboardButton("Paramètres", callback_data="parameters")
        ]
    },
    "lampesSelect": {
        "message": "Choisir la lampe:",
        "buttons": [
            InlineKeyboardButton(name.title(), callback_data=name)
            for name in ["chargeur", "commode", "bureau", "canapé", "ficus"]
        ]
    },
    "storesSelect": {
        "message": "Choisir le store:",
        "buttons": [
            InlineKeyboardButton(name.title(), callback_data=name)
            for name in ["Tous", "1", "2", "3", "4", "5"]
        ]
    },
    "parametersSelect": {
        "message": "Choisir le paramètre:",
        "buttons": [
            InlineKeyboardButton(name.title(), callback_data=name)
            for name in config['telegram']['bot']['settings']
        ]
    },
    "lampesAction": {
        "message": "Que faire avec la lampe:",
        "buttons": [
            InlineKeyboardButton("Allumer", callback_data="on"),
            InlineKeyboardButton("Éteindre", callback_data="off")
        ]
    },
    "storesAction": {
        "message": "Que faire avec le store:",
        "buttons": [
            InlineKeyboardButton("Monter", callback_data="up"),
            InlineKeyboardButton("Descendre", callback_data="down"),
            InlineKeyboardButton("Clac-clac", callback_data="clac"),
            InlineKeyboardButton("Stop", callback_data="stop")
        ]
    }
}
selection = {config['telegram']['users'][user]['chatId']:[] for user in config['telegram']['users']}

if __name__ == "__main__":
    main()
