import os
from tinydb import TinyDB, Query
from tinydb.operations import delete
from server.utils import loadYaml
from server import pb  # import printbetter from __init__.py


config = loadYaml("config")

# Initialize database
path = config['telegram']['database']['path'][os.environ["APP_SCOPE"]]
db = TinyDB(path)
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
        self.menuSelection = user['menuSelection']

    def __repr__(self):
        return f"{self['name']} ({self['id']})"

    def __getitem__(self, key):
        if key == "menuSelection":
            return self.menuSelection
        user = users.get(USER.id == self.id)
        return user[key]

    def __setitem__(self, key, value):
        users.update({key: value}, USER.id == self.id)

    def delete(self):
        pb.info(f"-> [database] Removed user {self}")
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
                  "menuSelection": [],
                  "settings": {
                      "lampes": {
                          "scheduler": False,
                          "success": False,
                          "errors": False
                          },
                      "stores": {
                          "scheduler": False,
                          "success": False,
                          "errors": False
                          },
                      "arrosage": {
                          "scheduler": False,
                          "success": False,
                          "errors": False
                          }
                  }},
                 USER.id == userId)
    pb.info(f"-> [database] New user created {name} ({userId})")


def isAuthorized(userId):
    user = users.get(USER.id == userId)
    if user:
        return user['authorized']


def getUsers():
    userTable = users.all()
    return [User(user['id']) for user in userTable]


def getAdminUsers():
    adminUsers = users.search(USER.admin == True)
    return [User(adminUser['id']) for adminUser in adminUsers]


def getNotifiedUsers(category, group):
    userTable = users.search(USER.settings[category][group] == True)
    return [User(user['id']) for user in userTable if user['authorized']]
