from database import users, USER

class User:
    def __init__(self, update):
        self.id = update.effective_user.id
        self.chatId = users.get(USER.id==self.id)["chatId"]

    def grantAdmin(self):
        users.update({"admin": True}, USER.id==self.id)

    def authorize(self):
        users.update({"authorized": True}, USER.id==self.id)

    def isAuthorized(self):
        user = users.search(USER.id == self.id)
        if user:
            return user["authorized"]
        else:
            return False

    def getMenuMessageId(self):
        user = users.get(USER.id == self.id)
        return user.get("menuMessagesId")

    def setMenuMessageId(self, messageId):
        users.update({"menuMessagesId": messageId}, USER.id == self.id)

    def delete(self):
        users.remove(USER.id == self.id)
