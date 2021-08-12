import telegram
import telegramBot
import telegramBot.database as db
from server import pb  # import printbetter from __init__.py


def notifyUsers(message, category, group):
    """Sends message to users that match notification group for specificied category."""
    users = db.getNotifiedUsers(category, group)
    for user in users:
        telegramBot.bot.send_message(user['chatId'], message, parse_mode=telegram.ParseMode.MARKDOWN)
    if users:
        pb.info(f"-> [telegram] Notified users: {', '.join([user['name'] for user in users])} / message: {message}")
