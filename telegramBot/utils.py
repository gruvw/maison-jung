import telegram
import telegramBot
import telegramBot.database as db


def notifyUsers(message, category, group):
    """Sends message to users that match notification group for specificied category."""
    users = db.getNotifiedUsers(category, group)
    for user in users:
        telegramBot.bot.send_message(user['chatId'], message, parse_mode=telegram.ParseMode.MARKDOWN)
