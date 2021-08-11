from copy import deepcopy
from telegram import InlineKeyboardButton
import telegramBot.database as db
from server.utils import loadYaml


options = loadYaml("options")


#########
# Menus #
#########

mainMenus = {
    "main": {
        "message": "Choisir le domaine:",
        "buttons": [
            InlineKeyboardButton("Lampes", callback_data="lampes"),
            InlineKeyboardButton("Stores", callback_data="stores"),
            InlineKeyboardButton("Arrosage", callback_data="arrosage"),
            InlineKeyboardButton("Paramètres", callback_data="settings")
        ],
        "n_cols": 2
    },
    "lampesSelect": {
        "message": "Choisir la lampe:",
        "buttons": [
            InlineKeyboardButton(lampe.title(), callback_data=lampe)
            for lampe in options['lampes']['names']
        ],
        "n_cols": 3
    },
    "lampesAction": {
        "message": "Que faire avec la lampe > {0}:",
        "buttons": [
            InlineKeyboardButton(action.title(), callback_data=data)
            for action, data in options['lampes']['actions'].items()
        ],
        "n_cols": 2
    },
    "storesSelect": {
        "message": "Choisir le store:",
        "buttons": [
            InlineKeyboardButton(store.title(), callback_data=store)
            for store in options['stores']['names']
        ],
        "n_cols": 4
    },
    "storesAction": {
        "message": "Que faire avec le store > {0}:",
        "buttons": [
            InlineKeyboardButton(action.title(), callback_data=data)
            for action, data in options['stores']['actions'].items()
        ],
        "n_cols": 2
    },
    "arrosageSelect": {
        "message": "Choisir la vanne:",
        "buttons": [
            InlineKeyboardButton(str(vanne), callback_data=vanne)
            for vanne in options['arrosage']['vannes']['names']
        ],
        "n_cols": 5
    },
    "arrosageAction": {
        "message": "Que faire avec la vanne > {0}:",
        "buttons": [
            InlineKeyboardButton(action.title(), callback_data=data)
            for action, data in options['arrosage']['vannes']['actions'].items()
        ],
        "n_cols": 2
    },
    "settingsSelect": {
        "message": "Choisir le paramètre:",
        "buttons": [
            InlineKeyboardButton(param.title(), callback_data=param)
            for param in ["lampes", "stores", "arrosage"]
        ],
        "n_cols": 2
    },
    "settingsAction": {
        "message": "Changer les notifications > {0}:",
        "buttons": [
            InlineKeyboardButton("🕑 Scheduler", callback_data="scheduler"),
            InlineKeyboardButton("👍 Success", callback_data="success"),
            InlineKeyboardButton("⚠️ Erreurs", callback_data="errors"),
        ],
        "n_cols": 2
    }
}


def getAdminMenus():
    # In a function because needs refresh from DB
    adminMenus = deepcopy(mainMenus)
    adminMenus['main']['buttons'].append(InlineKeyboardButton("Admin", callback_data="admin"))
    adminAddons = {
        "adminSelect": {
            "message": "Zone d'administration:",
            "buttons": [
                InlineKeyboardButton("Users", callback_data="admin,users")
            ],
            "n_cols": 1
        },
        "usersSelect": {
            "message": "Choisir l'utilisateur:",
            "buttons": [
                InlineKeyboardButton(f"{user['name']} ({user['id']})", callback_data=f"admin,{user['name']}-{user['id']}")
                for user in db.getUsers()
            ],
            "n_cols": 2
        },
        "usersAction": {
            "message": "Modifier les permissions de > {0}:",
            "buttons": [
                InlineKeyboardButton("Authorize", callback_data="admin,authorized"),
                InlineKeyboardButton("Admin", callback_data="admin,admin"),
                InlineKeyboardButton("🗑️ Delete", callback_data="admin,delete")
            ],
            "n_cols": 2
        },
    }
    adminMenus = {**adminMenus, **adminAddons}
    return adminMenus
