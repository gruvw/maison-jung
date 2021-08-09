import yaml


paths = {
    "config": "configs/configLocal.yml",
    "options": "telegramBot/options.yml",
}


def loadYaml(name):
    with open(paths[name], 'r') as stream:
        return yaml.safe_load(stream)


def boolToIcon(value, style="checkbox"):
    if style == "checkbox":
        return "✅" if value else "❌"
    if style == "light":
        return " 💡" if value else ""
    if style == "notification":
        return "🔔" if value else "🔕"
    if style == "water":
        return "💧" if value else ""

