from tinydb import TinyDB, Query
from tinydb.operations import delete

# Initialize database
db = TinyDB('telegramBot/database.json')
users = db.table('users')
USER = Query()

# Exceptions
class UserNotFound(Exception):
    """Raised if userId does not existes in DB."""
    pass


########
# User #
########

class User:
    def __init__(self, userId):
        user = users.get(USER.id == userId)
        if not user:
            raise UserNotFound(f"User id {userId} does not exists in database!")
        self.id = userId
        self.menuSelection = user["menuSelection"]

    def __repr__(self):
        return f"{self['name']} ({self['id']})"

    def __getitem__(self, key):
        if key == "menuSelection":
            return self.menuSelection
        user = users.get(USER.id == self.id)
        return user[key]

    def __setitem__(self, key, value):
        users.update({key: value}, USER.id == self.id)

    def saveSelection(self):
        self["menuSelection"] = self.menuSelection

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


def isAuthorized(userId):
    user = users.get(USER.id == userId)
    if user:
        return user["authorized"]


def getUsers():
    userTable = users.all()
    return [User(user["id"]) for user in userTable]


def getAdminUsers():
    adminUsers = users.search(USER.admin == True)
    return [User(adminUser["id"]) for adminUser in adminUsers]
