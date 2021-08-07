from tinydb import TinyDB, Query
from tinydb.operations import delete

# Initialize database
db = TinyDB('telegramBot/database.json')
users = db.table('users')
USER = Query()


########
# User #
########

class User:
    def __init__(self, update):
        self.id = update.effective_user.id
        self.chatId = users.get(USER.id == self.id)["chatId"]
        self.selection = users.get(USER.id == self.id)["menuSelection"]

    def authorize(self):
        users.update({"authorized": True}, USER.id == self.id)

    def isAuthorized(self):
        user = users.get(USER.id == self.id)
        return user["authorized"]

    def grantAdmin(self):
        users.update({"admin": True}, USER.id == self.id)

    def isAdmin(self):
        user = users.get(USER.id == self.id)
        return user["admin"]

    def setMenuMessageId(self, messageId):
        users.update({"menuMessagesId": messageId}, USER.id == self.id)

    def getMenuMessageId(self):
        user = users.get(USER.id == self.id)
        return user.get("menuMessagesId")

    def saveSelection(self):
        users.update({"menuSelection": self.selection}, USER.id == self.id)

    def delete(self):
        users.remove(USER.id == self.id)


###########
# Methods #
###########

def createUser(userId, chatId, name, authorized=False, admin=False):
    users.upsert({"id": userId,
                  "chatId": chatId,
                  "name": name,
                  "authorized": authorized,
                  "admin": admin,
                  "menuSelection": []},
                 USER.id == userId)


def getAuthorizedUsersId():
    authorizedUsers = users.search(USER.authorized == True)
    return [user["id"] for user in authorizedUsers]


def getUsers():
    userTable = users.all()
    result = [(user["name"], user["id"]) for user in userTable]
    return result
