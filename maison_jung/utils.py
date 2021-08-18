import yaml


paths = {
    "config": "config.yml",
    "options": "options.yml",
    "schedules": "schedules.yml",
    "database": "database.json",
}


def load_yaml(file_path):
    """Loads YAML file content."""
    with open(file_path, "r") as stream:
        return yaml.safe_load(stream)


def bool_to_icon(value, style="checkbox"):
    """Returns emoji based on boolean value."""
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

