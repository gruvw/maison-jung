import printbetter as pb
from tinydb import TinyDB, Query

from ..utils import load_yaml, paths


config = load_yaml(paths['config'])

# Initialize database
db = TinyDB(paths['database'])
users = db.table("users")
USER = Query()


# Exceptions
class UserNotFound(Exception):
    """Raised if user_id does not existes in DB."""
    pass


########
# User #
########

class User:
    def __init__(self, user_id):
        user = users.get(USER.id == user_id)
        if not user:
            raise UserNotFound(f"User id {user_id} does not exists in database!")
        self.id = user_id
        self.menu_selection = user['menu_selection']

    def __repr__(self):
        return f"{self['name']} ({self['id']})"

    def __getitem__(self, key):
        if key == "menu_selection":
            return self.menu_selection
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

def create_user(user_id, chat_id, name, authorized=False, admin=False):
    users.upsert({"id": user_id,
                  "chat_id": chat_id,
                  "name": name,
                  "authorized": authorized,
                  "admin": admin,
                  "menu_selection": [],
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
                 USER.id == user_id)
    pb.info(f"-> [database] New user created {name} ({user_id})")


def is_authorized(user_id):
    user = users.get(USER.id == user_id)
    if user:
        return user['authorized']


def get_users():
    user_table = users.all()
    return [User(user['id']) for user in user_table]


def get_admin_users():
    admin_users = users.search(USER.admin == True)
    return [User(admin_user['id']) for admin_user in admin_users]


def get_notified_users(category, group):
    user_table = users.search(USER.settings[category][group] == True)
    return [User(user['id']) for user in user_table if user['authorized']]
