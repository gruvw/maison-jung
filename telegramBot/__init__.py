import telegram
from copy import deepcopy
from functools import wraps
from telegram import ChatAction, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from server import files
from server.utils import loadYaml, boolToIcon
import telegramBot.actions
import telegramBot.database as db
from telegramBot.menus import mainMenus, getAdminMenus


config = loadYaml("config")


############
# Telegram #
############

# Telegram bot initialization
updater = Updater(token=config['telegram']['bot']['token'])
bot = updater.bot
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
            user['name'] = update.effective_user.name
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
                context.bot.send_message(user['chatId'], "You don't have the required permission.")
                return
            return func(update, context, user, *args, **kwargs)
        return wrapped
    return decorator


def buildMenu(buttons, n_cols):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    return menu


# Handlers

@commandHandler
@verify
def start(update, context):
    """/start handler"""
    user = update.effective_user
    chat = update.effective_chat
    if db.isAuthorized(user.id):
        context.bot.send_message(chat.id, "Your accont is authorized, bienvenue dans la maison Jung!")
        menu(update, context)
    else:
        context.bot.send_message(
            chat.id, "Your account is not authorized yet! An authorization request has been sent to administrators.")
        db.createUser(user.id, chat.id, user.name)


@commandHandler
@verify
@restricted("authorized")
def menu(update, context, user):
    """/menu handler"""
    try:
        oldMenuId = user['menuMessageId']
        user['menuSelection'] = []  # in order to use __setitem__
        try:
            context.bot.delete_message(user['chatId'], oldMenuId)
        except telegram.error.BadRequest:
            pass
    except KeyError:
        pass
    menu = getAdminMenus() if user['admin'] else mainMenus
    replyMarkup = InlineKeyboardMarkup(buildMenu(menu['main']['buttons'], n_cols=menu['main']['n_cols']))
    message = context.bot.send_message(user['chatId'], menu['main']['message'], reply_markup=replyMarkup)
    user['menuMessageId'] = message.message_id


@callbackHandler(patterns['mainMenu'])
@verify
@restricted("authorized")
def userCallback(update, context, user):
    """Callback function for authorized menu actions."""
    query = update.callback_query
    data = query.data
    query.answer()
    userMenuSelection = user['menuSelection']
    if data in userMenuSelection:  # prevents double clicks on buttons
        return
    userMenuSelection.append(data)
    if data == "home":
        menu(update, context)
        return
    elif len(userMenuSelection) == 1:
        scene = mainMenus[data+"Select"]
    elif len(userMenuSelection) == 2:
        scene = mainMenus[userMenuSelection[0]+"Action"]
    elif len(userMenuSelection) == 3:
        # Action
        context.bot.send_chat_action(user['chatId'], telegram.ChatAction.TYPING)
        telegramBot.actions.userAction(context.bot, user)
        menu(update, context)
        return
    buttons = scene['buttons']
    if userMenuSelection:
        # Adds home button
        buttons = [*deepcopy(buttons), InlineKeyboardButton("< Home", callback_data="home")]
        # Modify buttons' data
        if len(userMenuSelection) == 1:  # one button clicked
            if userMenuSelection[0] == "lampes":
                lampesState = files.getState("lampes")
                lampesState = [True if char == "A" else False for char in lampesState]
                for button, state in zip(buttons[:-1], lampesState):
                    button.text += " " + boolToIcon(state, style="light")
            elif userMenuSelection[0] == "arrosage":
                arrosageState = files.getState("arrosage")
                arrosageState = [True if char == "A" else False for char in arrosageState]
                for button, state in zip(buttons[:-1], arrosageState):
                    button.text += " " + boolToIcon(state, style="water")
            elif userMenuSelection[0] == "settings":
                userNotificationSettings = [any(user['settings'][setting].values()) for setting in user['settings']]
                for button, setting in zip(buttons[:-1], userNotificationSettings):
                    button.text += " " + boolToIcon(setting, style="notification")
        elif len(userMenuSelection) == 2:  # two buttons clicked
            if userMenuSelection[0] == "settings":
                selectedUserSettings = user['settings'][userMenuSelection[1]].values()
                for button, setting in zip(buttons[:-1], selectedUserSettings):
                    button.text += " " + boolToIcon(setting)
    message = scene['message'].format(f"_{userMenuSelection[1]}_") if len(userMenuSelection) == 2 else scene['message']
    replyMarkup = InlineKeyboardMarkup(buildMenu(buttons, n_cols=scene['n_cols']))
    query.message.edit_text(message, reply_markup=replyMarkup, parse_mode=telegram.ParseMode.MARKDOWN)
    user['menuSelection'] = userMenuSelection  # in order to use __setitem__


@callbackHandler(patterns['adminMenu'])
@verify
@restricted("admin")
def adminCallback(update, context, adminUser):
    """Callback function for admin menu actions."""
    query = update.callback_query
    data = query.data.split(',')[-1]
    query.answer()
    adminUserMenuSelection = adminUser['menuSelection']
    if data in adminUserMenuSelection:  # prevents double clicks on buttons
        return
    adminUserMenuSelection.append(data)
    if len(adminUserMenuSelection) in [1, 2]:
        scene = getAdminMenus()[data+"Select"]
    elif len(adminUserMenuSelection) == 3:
        scene = getAdminMenus()[adminUserMenuSelection[1]+"Action"]
    elif len(adminUserMenuSelection) == 4:
        # Action
        context.bot.send_chat_action(adminUser['chatId'], telegram.ChatAction.TYPING)
        telegramBot.actions.adminAction(context.bot, adminUser)
        try:
            menu(update, context)
        except db.UserNotFound:  # if admin deletes its own account
            pass
        return
    buttons = scene['buttons']
    if adminUserMenuSelection:
        # Adds home button
        buttons = [*deepcopy(buttons), InlineKeyboardButton("< Home", callback_data="home")]
        # Modify buttons' data
        if len(adminUserMenuSelection) == 3:  # three buttons clicked
            if adminUserMenuSelection[1] == "users":
                involvedUserId = int(adminUserMenuSelection[2].split("-")[-1])  # data exemple: @user-name-1234
                involvedUser = db.User(involvedUserId)
                buttons[0].text += " " + boolToIcon(involvedUser['authorized'])
                buttons[1].text += " " + boolToIcon(involvedUser['admin'])
    message = scene['message'].format(f"_{adminUserMenuSelection[2]}_") if len(adminUserMenuSelection) == 3 else scene['message']
    replyMarkup = InlineKeyboardMarkup(buildMenu(buttons, n_cols=scene['n_cols']))
    query.message.edit_text(message, reply_markup=replyMarkup, parse_mode=telegram.ParseMode.MARKDOWN)
    adminUser['menuSelection'] = adminUserMenuSelection  # in order to use __setitem__


########
# Main #
########

def main():
    updater.start_polling()
