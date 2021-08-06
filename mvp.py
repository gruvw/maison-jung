import yaml
from functools import wraps
import telegram
from telegram import ChatAction, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, commandhandler
import database as db


# Load config file
with open("config.yml", 'r') as stream:
    config = yaml.safe_load(stream)

############
# Telegram #
############

# Telegram bot initialization
updater = Updater(token=config['telegram']['bot']['token'])
dispatcher = updater.dispatcher


# Decorators and utilities
isAdminMenu = lambda data: "admin" in data

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


def noBot(func):
    """Prohibits access to robots."""
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        user = update.effective_user
        if user.is_bot:
            return
        return func(update, context, *args, **kwargs)
    return wrapped


def restrictedToAuthorizedUsers(func):
    """Restricts handler usage to authorized users."""
    @wraps(func)
    def wrapped(update, context):
        user = db.User(update)
        if not user.isAuthorized():
            context.bot.send_message(user.chatId, "Your account is not authorized!")
            return
        return func(update, context, user)
    return wrapped


def build_menu(buttons, n_cols):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    return menu


# Handlers

@commandHandler
@noBot
def start(update, context):
    user = update.effective_user
    chat = update.effective_chat
    if user.id in db.getAuthorizedUsersId():
        context.bot.send_message(chat.id, "Your accont is authorized, bienvenue dans la famille JUNG!")
    else:
        context.bot.send_message(chat.id, "Your account is not authorized yet! An authorization request has been sent to administrators.")
        db.createUser(user.id, chat.id, user.name)


@commandHandler
@noBot
@restrictedToAuthorizedUsers
def menu(update, context, user):
    oldMenuId = user.getMenuMessageId()
    if oldMenuId:
        context.user_data["selection"] = []
        context.bot.delete_message(user.chatId, oldMenuId)
    replyMarkup = InlineKeyboardMarkup(build_menu(menus["main"]["buttons"], n_cols=2))
    message = context.bot.send_message(user.chatId, menus["main"]["message"], reply_markup=replyMarkup)
    user.setMenuMessageId(message.message_id)


@callbackHandler
@noBot
@restrictedToAuthorizedUsers
def callback(update, context, user):
    # TODO current state display: lampes, arrosage, parametres
    query = update.callback_query
    data = query.data
    query.answer()
    context.user_data["selection"].append(data)
    if data == "home":
        scene = menus["main"]
        context.user_data["selection"].clear()
    if len(context.user_data["selection"]) == 1:
        scene = menus[data+"Select"]
    elif len(context.user_data["selection"]) == 2:
        scene = menus[context.user_data["selection"][0]+"Action"]
    elif len(context.user_data["selection"]) == 3:
        scene = menus["main"]
        context.bot.send_chat_action(user.chatId, telegram.ChatAction.TYPING)
        # ACTION
        context.bot.send_message(user.chatId, context.user_data["selection"])
        context.user_data["selection"].clear()
    buttons = scene["buttons"]
    if context.user_data["selection"]:
        buttons = [*buttons, InlineKeyboardButton("< Home", callback_data="home")]
    replyMarkup = InlineKeyboardMarkup(build_menu(buttons, n_cols=scene["n_cols"]))
    query.message.edit_text(scene["message"], reply_markup=replyMarkup)


########
# Main #
########

def main():
    updater.start_polling()
    updater.idle()


# TODO arrosageSelect, parametersAction, arrosageAction
menus = {
    "main": {
        "message": "Choisir le domaine:",
        "buttons": [
            InlineKeyboardButton("Lampes", callback_data="lampes"),
            InlineKeyboardButton("Stores", callback_data="stores"),
            InlineKeyboardButton("Arrosage", callback_data="arrosage"),
            InlineKeyboardButton("Paramètres", callback_data="parameters")
        ],
        "n_cols": 2
    },
    "lampesSelect": {
        "message": "Choisir la lampe:",
        "buttons": [
            InlineKeyboardButton(name.title(), callback_data=name)
            for name in ["chargeur", "commode", "bureau", "canapé", "ficus", "télé", "Lampe 7", "lampe 8", "lampe 9"]
        ],
        "n_cols": 3
    },
    "storesSelect": {
        "message": "Choisir le store:",
        "buttons": [
            InlineKeyboardButton(name.title(), callback_data=name)
            for name in ["maison", "étage", "rez", "bureau", "séjour 1", "séjour 2", "séjour 3", "séjour 4", "séjour 5", "zoé", "lucas", "arthur", "parents"]
        ],
        "n_cols": 4
    },
    "arrosageSelect": {
        "message": "Choisir la vanne:",
        "buttons": [
            InlineKeyboardButton(nb, callback_data=nb)
            for nb in range(1, 49)
        ],
        "n_cols": 5
    },
    "parametersSelect": {
        "message": "Choisir le paramètre:",
        "buttons": [
            InlineKeyboardButton(name.title(), callback_data=name)
            for name in ["lampes", "stores", "arrosage"]
        ],
        "n_cols": 2
    },
    "lampesAction": {
        "message": "Que faire avec la lampe:",
        "buttons": [
            InlineKeyboardButton("Allumer", callback_data="on"),
            InlineKeyboardButton("Éteindre", callback_data="off")
        ],
        "n_cols": 2
    },
    "storesAction": {
        "message": "Que faire avec le store:",
        "buttons": [
            InlineKeyboardButton("Monter", callback_data="up"),
            InlineKeyboardButton("Descendre", callback_data="down"),
            InlineKeyboardButton("Clac-clac", callback_data="clac"),
            InlineKeyboardButton("Stop", callback_data="stop")
        ],
        "n_cols": 2
    },
    "arrosageAction": {
        "message": "Que faire avec la vanne:",
        "buttons": [
            InlineKeyboardButton("Ouvrir", callback_data="open"),
            InlineKeyboardButton("Fermer", callback_data="close")
        ],
        "n_cols": 2
    }
}

if __name__ == "__main__":
    main()
