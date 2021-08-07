import telegramBot.database as db


def action(bot, user):
    """Dispatches actions."""
    if user["menuSelection"][0] == "":
        pass


def adminAction(bot, adminAgent):
    """Dispatches admin actions."""
    if adminAgent["menuSelection"][1] == "users":
        involvedUserId = int(adminAgent["menuSelection"][-2].split("-")[-1])  # data exemple: @user-name-1234
        action = adminAgent["menuSelection"][-1]
        editUsers(bot, adminAgent, involvedUserId, action)


def editUsers(bot, adminAgent, involvedUserId, action):
    """Modify user (admin only)."""
    involvedUser = db.User(involvedUserId)
    if action == "authorize":
        if involvedUser["authorized"]:
            for adminUser in db.getAdminUsers():  # broadcast to admins
                bot.send_message(adminUser["chatId"], f"❗ The user {involvedUser['name']} ({involvedUser['id']}) has had his **authorization** revoked by admin {adminAgent['name']}. ❗")
            bot.send_message(involvedUser["chatId"], "⛔ Your authorization has been revoked.")
            involvedUser["authorized"] = False  # revoke authorization
        else:
            for adminUser in db.getAdminUsers():  # broadcast to admins
                bot.send_message(adminUser["chatId"], f"❗ The user {involvedUser['name']} ({involvedUser['id']}) has been **authorized** by admin {adminAgent['name']}. ❗")
            bot.send_message(involvedUser["chatId"], "✅ You are now authorized.")
            involvedUser["authorized"] = True  # give authorization
    elif action == "admin":
        if involvedUser["admin"]:
            for adminUser in db.getAdminUsers():  # broadcast to admins
                bot.send_message(adminUser["chatId"], f"❗ The user {involvedUser['name']} ({involvedUser['id']}) has had his **admin permissions** revoked by admin {adminAgent['name']}. ❗")
            bot.send_message(involvedUser["chatId"], "⛔ Your admin permissions have been revoked.")
            involvedUser["admin"] = False  # revoke admin perms
        else:
            for adminUser in db.getAdminUsers():  # broadcast to admins
                bot.send_message(adminUser["chatId"], f"❗ The user {involvedUser['name']} ({involvedUser['id']}) has been given **admin permissions** by admin {adminAgent['name']}. ❗")
            bot.send_message(involvedUser["chatId"], "✅ You now have admin permissions.")
            involvedUser["admin"] = True  # give admin perms
    elif action == "delete":
        for adminUser in db.getAdminUsers():
            bot.send_message(adminUser["chatId"], f"❗ The user {involvedUser['name']} ({involvedUser['id']}) has been **deleted** by admin {adminAgent['name']}. ❗")
        bot.send_message(involvedUser["chatId"], "⛔ Your account has been deleted.")
        involvedUser.delete()
