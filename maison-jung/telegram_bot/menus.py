from telegram import InlineKeyboardButton

from . import database as db
from ..utils import load_yaml, paths


options = load_yaml(paths['options'])


#########
# Menus #
#########

def get_main_menus():
    """Returns main menus (authorized users only)."""
    main_menus = {
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
        "lampes_select": {
            "message": "Choisir la lampe:",
            "buttons": [
                InlineKeyboardButton(lampe.title(), callback_data=lampe)
                for lampe in options['lampes']['names']
            ],
            "n_cols": 3
        },
        "lampes_action": {
            "message": "Que faire avec la lampe > {0}:",
            "buttons": [
                InlineKeyboardButton(action.title(), callback_data=data)
                for action, data in options['lampes']['actions'].items()
            ],
            "n_cols": 2
        },
        "stores_select": {
            "message": "Choisir le store:",
            "buttons": [
                InlineKeyboardButton(store.title(), callback_data=store)
                for store in options['stores']['names']
            ],
            "n_cols": 4
        },
        "stores_action": {
            "message": "Que faire avec le store > {0}:",
            "buttons": [
                InlineKeyboardButton(action.title(), callback_data=data)
                for action, data in options['stores']['actions'].items()
            ],
            "n_cols": 2
        },
        "arrosage_select": {
            "message": "Choisir la vanne:",
            "buttons": [
                InlineKeyboardButton(str(vanne), callback_data=str(vanne))
                for vanne in options['arrosage']['vannes']['names']
            ],
            "n_cols": 5
        },
        "arrosage_action": {
            "message": "Que faire avec la vanne > {0}:",
            "buttons": [
                InlineKeyboardButton(action.title(), callback_data=data)
                for action, data in options['arrosage']['vannes']['actions'].items()
            ],
            "n_cols": 2
        },
        "settings_select": {
            "message": "Choisir le paramètre:",
            "buttons": [
                InlineKeyboardButton(param.title(), callback_data=param)
                for param in ["lampes", "stores", "arrosage"]
            ],
            "n_cols": 2
        },
        "settings_action": {
            "message": "Changer les notifications > {0}:",
            "buttons": [
                InlineKeyboardButton("🕑 Scheduler", callback_data="scheduler"),
                InlineKeyboardButton("👍 Success", callback_data="success"),
                InlineKeyboardButton("⚠️ Erreurs", callback_data="errors"),
            ],
            "n_cols": 2
        }
    }
    return main_menus


def get_admin_menus():
    """Returns admin menus (admin users only). (pulls data from database)"""
    admin_menus = get_main_menus()
    admin_menus['main']['buttons'].append(InlineKeyboardButton("Admin", callback_data="admin"))
    admin_addons = {
        "admin_select": {
            "message": "Zone d'administration:",
            "buttons": [
                InlineKeyboardButton("Users", callback_data="admin,users")
            ],
            "n_cols": 1
        },
        "users_select": {
            "message": "Choisir l'utilisateur:",
            "buttons": [
                InlineKeyboardButton(f"{user['name']} ({user['id']})", callback_data=f"admin,{user['name']}-{user['id']}")
                for user in db.get_users()
            ],
            "n_cols": 2
        },
        "users_action": {
            "message": "Modifier les permissions de > {0}:",
            "buttons": [
                InlineKeyboardButton("Authorize", callback_data="admin,authorized"),
                InlineKeyboardButton("Admin", callback_data="admin,admin"),
                InlineKeyboardButton("🗑️ Delete", callback_data="admin,delete")
            ],
            "n_cols": 2
        },
    }
    admin_menus = {**admin_menus, **admin_addons}
    return admin_menus
