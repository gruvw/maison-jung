from copy import deepcopy
from telegram import InlineKeyboardButton
import telegramBot.database as db


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
            InlineKeyboardButton("Paramètres", callback_data="parameters")
        ],
        "n_cols": 2
    },
    "lampesSelect": {
        "message": "Choisir la lampe:",
        "buttons": [
            InlineKeyboardButton(lampe.title(), callback_data=lampe)
            for lampe in ["chargeur", "commode", "bureau", "canapé", "ficus", "télé", "Lampe 7", "lampe 8", "lampe 9"]
        ],
        "n_cols": 3
    },
    "lampesAction": {
        "message": "Que faire avec la lampe > {0}:",
        "buttons": [
            InlineKeyboardButton("Allumer", callback_data="on"),
            InlineKeyboardButton("Éteindre", callback_data="off")
        ],
        "n_cols": 2
    },
    "storesSelect": {
        "message": "Choisir le store:",
        "buttons": [
            InlineKeyboardButton(store.title(), callback_data=store)
            for store in ["maison", "étage", "rez", "bureau", "séjour 1", "séjour 2", "séjour 3", "séjour 4", "séjour 5", "zoé", "lucas", "arthur", "parents"]
        ],
        "n_cols": 4
    },
    "storesAction": {
        "message": "Que faire avec le store > {0}:",
        "buttons": [
            InlineKeyboardButton("Monter", callback_data="up"),
            InlineKeyboardButton("Descendre", callback_data="down"),
            InlineKeyboardButton("Clac-clac", callback_data="clac"),
            InlineKeyboardButton("Stop", callback_data="stop")
        ],
        "n_cols": 2
    },
    "arrosageSelect": {
        "message": "Choisir la vanne:",
        "buttons": [
            InlineKeyboardButton(vanne, callback_data=vanne)
            for vanne in range(1, 49)
        ],
        "n_cols": 5
    },
    "arrosageAction": {
        "message": "Que faire avec la vanne > {0}:",
        "buttons": [
            InlineKeyboardButton("Ouvrir", callback_data="open"),
            InlineKeyboardButton("Fermer", callback_data="close")
        ],
        "n_cols": 2
    },
    "parametersSelect": {
        "message": "Choisir le paramètre:",
        "buttons": [
            InlineKeyboardButton(param.title(), callback_data=param)
            for param in ["lampes", "stores", "arrosage"]
        ],
        "n_cols": 2
    },
    "parametersAction": {
        "message": "Changer les notifications > {0}:",
        "buttons": [
            InlineKeyboardButton("Notifications", callback_data="notifications"),
            InlineKeyboardButton("Scheduler", callback_data="scheduler"),
            InlineKeyboardButton("Errors", callback_data="errors"),
        ],
        "n_cols": 2
    }
}

adminMenus = deepcopy(mainMenus)
adminMenus["main"]["buttons"].append(InlineKeyboardButton("Admin", callback_data="admin"))
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
            InlineKeyboardButton(f"{name}: {userId}", callback_data=f"admin,{name}-{userId}")
            for name, userId in db.getUsers()
        ],
        "n_cols": 2
    },
    "usersAction": {
        "message": "Modifier les permissions de > {0}:",
        "buttons": [
            InlineKeyboardButton("Authorize", callback_data="admin,authorize"),
            InlineKeyboardButton("Admin", callback_data="admin,admin"),
            InlineKeyboardButton("Delete", callback_data="admin,delete")
        ],
        "n_cols": 2
    },
}
adminMenus = adminMenus | adminAddons
