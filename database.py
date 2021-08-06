from tinydb import TinyDB, Query
from tinydb.operations import delete

# Initialize database
db = TinyDB('database.json')
users = db.table('users')
USER = Query()

# Operations
def appendMenuMessageId(messageId):
    def transform(document):
        document["menuMessagesId"].append(messageId)
    return transform

def removeMenuMessageId(messageId):
    def transform(document):
        document["menuMessagesId"].remove(messageId)
    return transform

########
# User #
########

class User:
    def __init__(self, update):
        self.id = update.effective_user.id
        self.chatId = users.get(USER.id==self.id)["chatId"]

    def grantAdmin(self):
        users.update({"admin": True}, USER.id==self.id)

    def authorize(self):
        users.update({"authorized": True}, USER.id==self.id)

    def isAuthorized(self):
        user = users.get(USER.id == self.id)
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


###########
# Methods #
###########

def createUser(userId, chatId, name, authorized=False, admin=False):
    if not users.get(USER.id==userId):
        users.insert({"id": userId,
                      "chatId": chatId,
                      "name": name,
                      "authorized": authorized,
                      "admin": admin})

def getAuthorizedUsersId():
    authorizedUsers = users.search(USER.authorized == True)
    return [user["id"] for user in authorizedUsers]

