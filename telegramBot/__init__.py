import yaml
import telegram
from functools import wraps
from telegram import ChatAction, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, commandhandler
import telegramBot.database as db
from telegramBot.menus import mainMenus, adminMenus


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

patterns = {
    "mainMenu": lambda data: "admin" not in data,
    "adminMenu": lambda data: "admin" in data,
}


def commandHandler(func):
    """Registers a function as a command handler."""
    handler = CommandHandler(func.__name__, func)
    dispatcher.add_handler(handler)
    return func


def callbackHandler(pattern=None):
    """Registers a function as a callback handler."""
    def decorator(func):
        handler = CallbackQueryHandler(func, pattern=pattern)
        dispatcher.add_handler(handler)
        return func
    return decorator


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
    def wrapped(update, context, *args, **kwargs):
        user = db.User(update)
        if not user.isAuthorized():
            update.callback_query.answer()
            context.bot.send_message(user.chatId, "Your account is not authorized!")
            return
        return func(update, context, user, *args, **kwargs)
    return wrapped


def restrictedToAdminUsers(func):
    """Restricts handler usage to admin users."""
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        user = db.User(update)
        if not user.isAdmin():
            update.callback_query.answer()
            context.bot.send_message(user.chatId, "Your account is not admin!")
            return
        return func(update, context, user, *args, **kwargs)
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
        menu(update, context)
    else:
        context.bot.send_message(
            chat.id, "Your account is not authorized yet! An authorization request has been sent to administrators.")
        db.createUser(user.id, chat.id, user.name)


@commandHandler
@noBot
@restrictedToAuthorizedUsers
def menu(update, context, user):
    oldMenuId = user.getMenuMessageId()
    if oldMenuId:
        user.selection.clear()
        user.saveSelection()
        try:
            context.bot.delete_message(user.chatId, oldMenuId)
        except telegram.error.BadRequest:
            pass
    menu = adminMenus if user.isAdmin() else mainMenus
    replyMarkup = InlineKeyboardMarkup(build_menu(menu["main"]["buttons"], n_cols=menu["main"]["n_cols"]))
    message = context.bot.send_message(user.chatId, menu["main"]["message"], reply_markup=replyMarkup)
    user.setMenuMessageId(message.message_id)


@callbackHandler(patterns["mainMenu"])
@noBot
@restrictedToAuthorizedUsers
def authorizedCallback(update, context, user):
    # TODO current state display: lampes, arrosage, parametres
    query = update.callback_query
    data = query.data
    query.answer()
    user.selection.append(data)
    user.saveSelection()
    if data == "home":
        menu(update, context)
        return
    elif len(user.selection) == 1:
        scene = mainMenus[data+"Select"]
    elif len(user.selection) == 2:
        scene = mainMenus[user.selection[-2]+"Action"]
    elif len(user.selection) == 3:
        context.bot.send_chat_action(user.chatId, telegram.ChatAction.TYPING)
        # TODO ACTION
        context.bot.send_message(user.chatId, user.selection)
        menu(update, context)
        return
    buttons = scene["buttons"]
    if user.selection:
        buttons = [*buttons, InlineKeyboardButton("< Home", callback_data="home")]
    message = scene["message"].format(user.selection[-1]) if len(user.selection) == 2 else scene["message"]
    replyMarkup = InlineKeyboardMarkup(build_menu(buttons, n_cols=scene["n_cols"]))
    query.message.edit_text(message, reply_markup=replyMarkup)


@callbackHandler(patterns["adminMenu"])
@noBot
@restrictedToAdminUsers
def adminCallback(update, context, user):
    # TODO current state display: user perm
    query = update.callback_query
    data = query.data.split(',')[-1]
    query.answer()
    user.selection.append(data)
    user.saveSelection()
    if len(user.selection) in [1, 2]:
        scene = adminMenus[data+"Select"]
    elif len(user.selection) == 3:
        scene = adminMenus[user.selection[-2]+"Action"]
    elif len(user.selection) == 4:
        context.bot.send_chat_action(user.chatId, telegram.ChatAction.TYPING)
        # TODO ACTION
        context.bot.send_message(user.chatId, user.selection[1:])
        menu(update, context)
        return
    buttons = scene["buttons"]
    if user.selection:
        buttons = [*buttons, InlineKeyboardButton("< Home", callback_data="home")]
    message = scene["message"].format(user.selection[-1]) if len(user.selection) == 3 else scene["message"]
    replyMarkup = InlineKeyboardMarkup(build_menu(buttons, n_cols=scene["n_cols"]))
    query.message.edit_text(message, reply_markup=replyMarkup)


########
# Main #
########

def main():
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
