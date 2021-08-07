import yaml
import telegram
from copy import deepcopy
from functools import wraps
from telegram import ChatAction, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, commandhandler
import telegramBot.database as db
from telegramBot.menus import mainMenus, getAdminMenus
from telegramBot.actions import action, adminAction


# Load config file
with open("config.yml", 'r') as stream:
    config = yaml.safe_load(stream)

# Utilities
def boolToIcon(value):
    return "✅" if value else "❌"


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


def verify(func):
    """Prohibits access to robots & updates user informations."""
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        if update.effective_user.is_bot:
            return
        try:
            user = db.User(update.effective_user.id)
            user["name"] = update.effective_user.name
        except db.UserNotFound:
            pass
        return func(update, context, *args, **kwargs)
    return wrapped


def restricted(permission):
    """Restricts handler usage to authorized users."""
    def decorator(func):
        @wraps(func)
        def wrapped(update, context, *args, **kwargs):
            user = db.User(update.effective_user.id)
            if not user[permission]:
                context.bot.send_message(user["chatId"], "You don't have the required permission.")
                return
            return func(update, context, user, *args, **kwargs)
        return wrapped
    return decorator


def build_menu(buttons, n_cols):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    return menu


# Handlers

@commandHandler
@verify
def start(update, context):
    user = update.effective_user
    chat = update.effective_chat
    if db.isAuthorized(user.id):
        context.bot.send_message(chat.id, "Your accont is authorized, bienvenue dans la famille JUNG!")
        menu(update, context)
    else:
        context.bot.send_message(
            chat.id, "Your account is not authorized yet! An authorization request has been sent to administrators.")
        db.createUser(user.id, chat.id, user.name)


@commandHandler
@verify
@restricted("authorized")
def menu(update, context, user):
    try:
        oldMenuId = user["menuMessageId"]
        user["menuSelection"].clear()
        try:
            context.bot.delete_message(user["chatId"], oldMenuId)
        except telegram.error.BadRequest:
            pass
    except KeyError:
        pass
    menu = getAdminMenus() if user["admin"] else mainMenus
    replyMarkup = InlineKeyboardMarkup(build_menu(menu["main"]["buttons"], n_cols=menu["main"]["n_cols"]))
    message = context.bot.send_message(user["chatId"], menu["main"]["message"], reply_markup=replyMarkup)
    user["menuMessageId"] = message.message_id
    user.saveSelection()


@callbackHandler(patterns["mainMenu"])
@verify
@restricted("authorized")
def authorizedCallback(update, context, user):
    # TODO current state display: lampes, arrosage, parametres
    query = update.callback_query
    data = query.data
    query.answer()
    user["menuSelection"].append(data)
    if data == "home":
        menu(update, context)
        return
    elif len(user["menuSelection"]) == 1:
        scene = mainMenus[data+"Select"]
    elif len(user["menuSelection"]) == 2:
        scene = mainMenus[user["menuSelection"][-2]+"Action"]
    elif len(user["menuSelection"]) == 3:
        # action
        context.bot.send_chat_action(user["chatId"], telegram.ChatAction.TYPING)
        action(context.bot, user)
        context.bot.send_message(user["chatId"], user["menuSelection"])
        menu(update, context)
        return
    buttons = scene["buttons"]
    if user["menuSelection"]:
        buttons = [*deepcopy(buttons), InlineKeyboardButton("< Home", callback_data="home")]
    message = scene["message"].format(user["menuSelection"][-1]) if len(user["menuSelection"]) == 2 else scene["message"]
    replyMarkup = InlineKeyboardMarkup(build_menu(buttons, n_cols=scene["n_cols"]))
    query.message.edit_text(message, reply_markup=replyMarkup)
    user.saveSelection()


@callbackHandler(patterns["adminMenu"])
@verify
@restricted("admin")
def adminCallback(update, context, adminUser):
    query = update.callback_query
    data = query.data.split(',')[-1]
    query.answer()
    adminUser["menuSelection"].append(data)
    if len(adminUser["menuSelection"]) in [1, 2]:
        scene = getAdminMenus()[data+"Select"]
    elif len(adminUser["menuSelection"]) == 3:
        scene = getAdminMenus()[adminUser["menuSelection"][-2]+"Action"]
    elif len(adminUser["menuSelection"]) == 4:
        # action
        context.bot.send_chat_action(adminUser["chatId"], telegram.ChatAction.TYPING)
        adminAction(context.bot, adminUser)
        menu(update, context)
        return
    buttons = scene["buttons"]
    if adminUser["menuSelection"]:
        # Adds home button
        buttons = [*deepcopy(buttons), InlineKeyboardButton("< Home", callback_data="home")]
        # Modify buttons' data
        if len(adminUser["menuSelection"]) == 3:
            if adminUser["menuSelection"][-2] == "users":
                involvedUserId = int(adminUser["menuSelection"][-1].split("-")[-1])  # data exemple: @user-name-1234
                involvedUser = db.User(involvedUserId)
                buttons[0].text = boolToIcon(involvedUser["authorized"]) + " " + buttons[0].text
                buttons[1].text = boolToIcon(involvedUser["admin"]) + " " + buttons[1].text
    message = scene["message"].format(adminUser["menuSelection"][-1]) if len(adminUser["menuSelection"]) == 3 else scene["message"]
    replyMarkup = InlineKeyboardMarkup(build_menu(buttons, n_cols=scene["n_cols"]))
    query.message.edit_text(message, reply_markup=replyMarkup)
    adminUser.saveSelection()


########
# Main #
########

def main():
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
