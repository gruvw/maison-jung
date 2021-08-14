import printbetter as pb
import telegram

from . import database as db
from .core import bot
from .. import server
from ..utils import bool_to_icon, load_yaml, paths


config = load_yaml(paths['config'])
options = load_yaml(paths['options'])


def user_action(user_agent):
    """Dispatches user actions. (authorized only)"""
    selection = user_agent['menu_selection']
    if selection[0] == "lampes":
        data = list(config['adafruit']['feeds']['defaults']['lampes'])
        data[options['lampes']['names'].index(selection[1])] = selection[2]
        if not server.actions.lampes(''.join(data), f"telegram {user_agent['name']}"):
            bot.send_message(user_agent['chat_id'], "⚠️ Une erreur est survenue.")
    elif selection[0] == "stores":
        data = options['stores']['names'][selection[1]]
        data = data.replace("_", selection[2])
        if not server.actions.stores(data, f"telegram {user_agent['name']}"):
            bot.send_message(user_agent['chat_id'], "⚠️ Une erreur est survenue.")
    elif selection[0] == "arrosage":
        data = selection[1] + selection[2]
        data = data if len(data) == 3 else "0" + data
        if not server.actions.arrosage(data, f"telegram {user_agent['name']}"):
            bot.send_message(user_agent['chat_id'], "⚠️ Une erreur est survenue.")
    elif selection[0] == "settings":
        # Toggle setting state
        user_agent_settings = user_agent['settings']
        new_state = not user_agent_settings[selection[1]][selection[2]]
        user_agent_settings[selection[1]][selection[2]] = new_state
        user_agent['settings'] = user_agent_settings  # in order to use __setitem__
        pb.info(f"-> [telegram] User {user_agent} changed his notifications settings: {selection[1]}/{selection[2]} -> {new_state}")
        bot.send_message(user_agent['chat_id'],
                         f"🔔 Les notifications _{selection[1]}_ -> _{selection[2]}_ sont maintenant: {bool_to_icon(new_state)}", parse_mode=telegram.ParseMode.MARKDOWN)


def admin_action(admin_agent):
    """Dispatches admin actions. (admin only)"""
    if admin_agent['menu_selection'][1] == "users":
        involved_user_id = int(admin_agent['menu_selection'][-2].split("-")[-1])  # data exemple: @user-name-1234
        action = admin_agent['menu_selection'][-1]
        edit_users(admin_agent, involved_user_id, action)


def edit_users(admin_agent, involved_user_id, action):
    """Modifies user permissions. (admin only)"""
    involved_user = db.User(involved_user_id)
    if action == "authorized":
        pb.info(f"-> [telegram] Admin user {admin_agent} changed permissions of user {involved_user}: authorized -> {not involved_user['authorized']}")
        if involved_user['authorized']:
            for admin_user in db.get_admin_users():  # broadcast to admins
                bot.send_message(admin_user['chat_id'],
                                 f"❗ The user {involved_user['name']} ({involved_user['id']}) has had his **authorization** revoked by admin {admin_agent['name']}.", parse_mode=telegram.ParseMode.MARKDOWN)
            bot.send_message(involved_user['chat_id'], "⛔ Your authorization has been revoked.")
            involved_user['authorized'] = False  # revoke authorization
            involved_user['admin'] = False  # revoking authorization also revokes admin perms
        else:
            for admin_user in db.get_admin_users():  # broadcast to admins
                bot.send_message(admin_user['chat_id'],
                                 f"❗ The user {involved_user['name']} ({involved_user['id']}) has been **authorized** by admin {admin_agent['name']}.", parse_mode=telegram.ParseMode.MARKDOWN)
            bot.send_message(involved_user['chat_id'], "✅ You are now authorized.")
            involved_user['authorized'] = True  # give authorization
    elif action == "admin":
        pb.info(f"-> [telegram] Admin user {admin_agent} changed permissions of user {involved_user}: admin -> {not involved_user['admin']}")
        if involved_user['admin']:
            for admin_user in db.get_admin_users():  # broadcast to admins
                bot.send_message(admin_user['chat_id'],
                                 f"❗ The user {involved_user['name']} ({involved_user['id']}) has had his **admin permissions** revoked by admin {admin_agent['name']}.", parse_mode=telegram.ParseMode.MARKDOWN)
            bot.send_message(involved_user['chat_id'], "⛔ Your admin permissions have been revoked.")
            involved_user['admin'] = False  # revoke admin perms
        else:
            for admin_user in db.get_admin_users():  # broadcast to admins
                bot.send_message(admin_user['chat_id'],
                                 f"❗ The user {involved_user['name']} ({involved_user['id']}) has been given **admin permissions** by admin {admin_agent['name']}.", parse_mode=telegram.ParseMode.MARKDOWN)
            bot.send_message(involved_user['chat_id'], "✅ You now have admin permissions.")
            involved_user['admin'] = True  # give admin perms
    elif action == "delete":
        pb.info(f"-> [telegram] Admin user {admin_agent} deleted user {involved_user}")
        for admin_user in db.get_admin_users():
            bot.send_message(admin_user['chat_id'],
                             f"❗ The user {involved_user['name']} ({involved_user['id']}) has been **deleted** by admin {admin_agent['name']}.", parse_mode=telegram.ParseMode.MARKDOWN)
        try:  # delete his old menu
            old_menu_id = involved_user['menu_message_id']
            try:
                bot.delete_message(involved_user['chat_id'], old_menu_id)
            except telegram.error.BadRequest:
                pass
        except KeyError:
            pass
        bot.send_message(involved_user['chat_id'],
                         "⛔ Your account has been deleted. Use the `/start` command if you think that it was a mistake.", parse_mode=telegram.ParseMode.MARKDOWN)
        involved_user.delete()


def notify_users(message, category, group):
    """Sends message to users that match notification group for specificied category."""
    users = db.get_notified_users(category, group)
    for user in users:
        bot.send_message(user['chat_id'], message, parse_mode=telegram.ParseMode.MARKDOWN)
    if users:
        pb.info(f"-> [telegram] Notified users: {', '.join([user['name'] for user in users])} / message: {message}")
