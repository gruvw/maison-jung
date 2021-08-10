import yaml


paths = {
    "config": "configs/configLocal.yml",
    "options": "telegramBot/options.yml",
}


def loadYaml(name):
    """Loads YAML file content."""
    with open(paths[name], 'r') as stream:
        return yaml.safe_load(stream)


def boolToIcon(value, style="checkbox"):
    """Return emoji base on boolean value."""
    if style == "checkbox":
        return "✅" if value else "❌"
    if style == "light":
        return " 💡" if value else ""
    if style == "notification":
        return "🔔" if value else "🔕"
    if style == "water":
        return "💧" if value else ""
    if style == "clock":
        return "🕑" if value else ""

