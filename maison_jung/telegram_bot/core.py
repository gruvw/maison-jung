import printbetter as pb
import telegram
import uuid
from copy import deepcopy
from functools import wraps
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

from .. import telegram_bot
from ..server import files
from ..telegram_bot import database as db, menus
from ..utils import bool_to_icon, load_yaml, paths


config = load_yaml(paths['config'])

# Telegram bot initialization
updater = Updater(token=config['telegram']['bot']['token'])
bot = updater.bot
dispatcher = updater.dispatcher


# Decorators and utilities

patterns = {
    "main_menu": lambda data: "admin" not in data,
    "admin_menu": lambda data: "admin" in data,
}


def command_handler(func):
    """Registers a function as a command handler."""
    handler = CommandHandler(func.__name__, func)
    dispatcher.add_handler(handler)
    return func


def callback_handler(pattern=None):
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
                context.bot.send_message(user['chat_id'], "You don't have the required permission.")
                return
            return func(update, context, user, *args, **kwargs)
        return wrapped
    return decorator


def build_menu(buttons, n_cols):
    """Appends unique id to each button and builds telegram menu."""
    uid = uuid.uuid4()
    for button in buttons:
        button.callback_data += f"/{uid}"
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    return menu


# Handlers

@command_handler
@verify
def start(update, context):
    """/start handler"""
    user = update.effective_user
    chat = update.effective_chat
    pb.info(f"<- [telegram] User id {user.id} executed /start")
    if db.is_authorized(user.id):
        context.bot.send_message(chat.id, "Your accont is authorized, bienvenue dans la maison Jung!")
        menu(update, context)
    else:
        context.bot.send_message(chat.id,
                                 "Your account is not authorized yet! An authorization request has been sent to administrators.")
        db.create_user(user.id, chat.id, user.name)


@command_handler
@verify
@restricted("authorized")
def menu(update, context, user):
    """/menu handler"""
    try:
        old_menu_id = user['menu_message_id']
        user['menu_selection'] = []  # in order to use __setitem__
        try:
            context.bot.delete_message(user['chat_id'], old_menu_id)
        except telegram.error.BadRequest:
            pass
    except KeyError:
        pass
    menu = menus.get_admin_menus() if user['admin'] else menus.get_main_menus()
    reply_markup = InlineKeyboardMarkup(build_menu(menu['main']['buttons'], menu['main']['n_cols']))
    message = context.bot.send_message(user['chat_id'], menu['main']['message'], reply_markup=reply_markup)
    user['menu_message_id'] = message.message_id


@callback_handler(patterns['main_menu'])
@verify
@restricted("authorized")
def user_callback(update, context, user):
    """Callback function for authorized menu actions."""
    query = update.callback_query
    data, menu_uid = query.data.rsplit("/", 1)
    query.answer()
    if data == "home":
        menu(update, context)
        return
    try:
        if menu_uid == user['old_menu_uid']:  # prevents double clicks on buttons
            return
    except KeyError:
        pass
    user['old_menu_uid'] = menu_uid  # stores old menu uid, next click should not have the same
    user_menu_selection = user['menu_selection']
    user_menu_selection.append(data)
    if len(user_menu_selection) == 1:
        scene = menus.get_main_menus()[data+"_select"]
    elif len(user_menu_selection) == 2:
        scene = menus.get_main_menus()[user_menu_selection[0]+"_action"]
    elif len(user_menu_selection) == 3:
        # Action
        context.bot.send_chat_action(user['chat_id'], telegram.ChatAction.TYPING)
        telegram_bot.actions.user_action(user)
        menu(update, context)
        return
    buttons = scene['buttons']
    if user_menu_selection:
        # Adds home button
        buttons = [*deepcopy(buttons), InlineKeyboardButton("< Home", callback_data="home")]
        # Modify buttons' data
        if len(user_menu_selection) == 1:  # one button clicked
            if user_menu_selection[0] == "lampes":
                lampes_state = files.get_state("lampes")
                lampes_state = [True if char == "A" else False for char in lampes_state]
                for button, state in zip(buttons[:-1], lampes_state):
                    button.text += " " + bool_to_icon(state, style="light")
            elif user_menu_selection[0] == "arrosage":
                arrosage_state = files.get_state("arrosage")
                arrosage_state = [True if char == "A" else False for char in arrosage_state]
                for button, state in zip(buttons[:-1], arrosage_state):
                    button.text += " " + bool_to_icon(state, style="water")
            elif user_menu_selection[0] == "settings":
                user_notification_settings = [any(user['settings'][setting].values()) for setting in user['settings']]
                for button, setting in zip(buttons[:-1], user_notification_settings):
                    button.text += " " + bool_to_icon(setting, style="notification")
        elif len(user_menu_selection) == 2:  # two buttons clicked
            if user_menu_selection[0] == "settings":
                selected_user_settings = user['settings'][user_menu_selection[1]].values()
                for button, setting in zip(buttons[:-1], selected_user_settings):
                    button.text += " " + bool_to_icon(setting)
    message = scene['message'].format(f"_{user_menu_selection[1]}_") if len(user_menu_selection) == 2 else scene['message']
    reply_markup = InlineKeyboardMarkup(build_menu(buttons, scene['n_cols']))
    query.message.edit_text(message, reply_markup=reply_markup, parse_mode=telegram.ParseMode.MARKDOWN)
    user['menu_selection'] = user_menu_selection  # in order to use __setitem__


@callback_handler(patterns['admin_menu'])
@verify
@restricted("admin")
def admin_callback(update, context, admin_user):
    """Callback function for admin menu actions."""
    query = update.callback_query
    data, menu_uid = query.data.rsplit("/", 1)
    data = data.split(',')[-1]  # removes admin prefix
    query.answer()
    try:
        if menu_uid == admin_user['old_menu_uid']:  # prevents double clicks on buttons
            return
    except KeyError:
        pass
    admin_user['old_menu_uid'] = menu_uid  # stores old menu uid, next click should not have the same
    admin_user_menu_selection = admin_user['menu_selection']
    admin_user_menu_selection.append(data)
    if len(admin_user_menu_selection) in [1, 2]:
        scene = menus.get_admin_menus()[data+"_select"]
    elif len(admin_user_menu_selection) == 3:
        scene = menus.get_admin_menus()[admin_user_menu_selection[1]+"_action"]
    elif len(admin_user_menu_selection) == 4:
        # Action
        context.bot.send_chat_action(admin_user['chat_id'], telegram.ChatAction.TYPING)
        telegram_bot.actions.admin_action(admin_user)
        try:
            menu(update, context)
        except db.UserNotFound:  # if admin deletes its own account
            pass
        return
    buttons = scene['buttons']
    if admin_user_menu_selection:
        # Adds home button
        buttons = [*deepcopy(buttons), InlineKeyboardButton("< Home", callback_data="home")]
        # Modify buttons' data
        if len(admin_user_menu_selection) == 3:  # three buttons clicked
            if admin_user_menu_selection[1] == "users":
                involved_user_id = int(admin_user_menu_selection[2].split("-")[-1])  # data exemple: @user-name-1234
                involved_user = db.User(involved_user_id)
                buttons[0].text += " " + bool_to_icon(involved_user['authorized'])
                buttons[1].text += " " + bool_to_icon(involved_user['admin'])
    message = scene['message'].format(f"_{admin_user_menu_selection[2]}_") if len(admin_user_menu_selection) == 3 else scene['message']
    reply_markup = InlineKeyboardMarkup(build_menu(buttons, scene['n_cols']))
    query.message.edit_text(message, reply_markup=reply_markup, parse_mode=telegram.ParseMode.MARKDOWN)
    admin_user['menu_selection'] = admin_user_menu_selection  # in order to use __setitem__
