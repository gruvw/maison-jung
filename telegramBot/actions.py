import telegram
import telegramBot.database as db
import server.actions
from server.utils import loadYaml, boolToIcon


config = loadYaml("config")
options = loadYaml("options")


def userAction(bot, userAgent):
    """Dispatches user actions. (authorized only)"""
    selection = userAgent['menuSelection']
    if selection[0] == "lampes":
        data = list(config['adafruit']['feeds']['defaults']['lampes'])
        data[int(options['lampes']['names'][selection[1]])] = selection[2]
        if not server.actions.lampes(''.join(data), "telegram"):
            bot.send_message(userAgent['chatId'], "⚠️ Une erreur est survenue.")
    elif selection[0] == "stores":
        data = options['stores']['names'][selection[1]]
        data = data.replace("_", selection[2])
        if not server.actions.stores(data, "telegram"):
            bot.send_message(userAgent['chatId'], "⚠️ Une erreur est survenue.")
    elif selection[0] == "arrosage":
        data = selection[1] + selection[2]
        data = data if len(data) == 3 else "0" + data
        if not server.actions.arrosage(data, "telegram"):
            bot.send_message(userAgent['chatId'], "⚠️ Une erreur est survenue.")
    elif selection[0] == "settings":
        # toggle setting state
        userAgentSettings = userAgent['settings']
        newState = not userAgentSettings[selection[1]][selection[2]]
        userAgentSettings[selection[1]][selection[2]] = newState
        userAgent['settings'] = userAgentSettings  # in order to use __setitem__
        bot.send_message(userAgent['chatId'],
                         f"🔔 Les notifications _{selection[1]}_ -> _{selection[2]}_ sont maintenant: {boolToIcon(newState)}", parse_mode=telegram.ParseMode.MARKDOWN)


def adminAction(bot, adminAgent):
    """Dispatches admin actions. (admin only)"""
    if adminAgent['menuSelection'][1] == "users":
        involvedUserId = int(adminAgent['menuSelection'][-2].split("-")[-1])  # data exemple: @user-name-1234
        action = adminAgent['menuSelection'][-1]
        editUsers(bot, adminAgent, involvedUserId, action)


def editUsers(bot, adminAgent, involvedUserId, action):
    """Modify user permissions. (admin only)"""
    involvedUser = db.User(involvedUserId)
    if action == "authorize":
        if involvedUser['authorized']:
            for adminUser in db.getAdminUsers():  # broadcast to admins
                bot.send_message(adminUser['chatId'],
                                 f"❗ The user {involvedUser['name']} ({involvedUser['id']}) has had his **authorization** revoked by admin {adminAgent['name']}.", parse_mode=telegram.ParseMode.MARKDOWN)
            bot.send_message(involvedUser['chatId'], "⛔ Your authorization has been revoked.")
            involvedUser['authorized'] = False  # revoke authorization
        else:
            for adminUser in db.getAdminUsers():  # broadcast to admins
                bot.send_message(adminUser['chatId'],
                                 f"❗ The user {involvedUser['name']} ({involvedUser['id']}) has been **authorized** by admin {adminAgent['name']}.", parse_mode=telegram.ParseMode.MARKDOWN)
            bot.send_message(involvedUser['chatId'], "✅ You are now authorized.")
            involvedUser['authorized'] = True  # give authorization
    elif action == "admin":
        if involvedUser['admin']:
            for adminUser in db.getAdminUsers():  # broadcast to admins
                bot.send_message(adminUser['chatId'],
                                 f"❗ The user {involvedUser['name']} ({involvedUser['id']}) has had his **admin permissions** revoked by admin {adminAgent['name']}.", parse_mode=telegram.ParseMode.MARKDOWN)
            bot.send_message(involvedUser['chatId'], "⛔ Your admin permissions have been revoked.")
            involvedUser['admin'] = False  # revoke admin perms
        else:
            for adminUser in db.getAdminUsers():  # broadcast to admins
                bot.send_message(adminUser['chatId'],
                                 f"❗ The user {involvedUser['name']} ({involvedUser['id']}) has been given **admin permissions** by admin {adminAgent['name']}.", parse_mode=telegram.ParseMode.MARKDOWN)
            bot.send_message(involvedUser['chatId'], "✅ You now have admin permissions.")
            involvedUser['admin'] = True  # give admin perms
    elif action == "delete":
        for adminUser in db.getAdminUsers():
            bot.send_message(adminUser['chatId'],
                             f"❗ The user {involvedUser['name']} ({involvedUser['id']}) has been **deleted** by admin {adminAgent['name']}.", parse_mode=telegram.ParseMode.MARKDOWN)
        bot.send_message(involvedUser['chatId'],
                         "⛔ Your account has been deleted. Use the `/start` command if you think that it was a mistake.", parse_mode=telegram.ParseMode.MARKDOWN)
        involvedUser.delete()
