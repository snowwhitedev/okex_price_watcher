import simplejson as json
import time

SETTINS_JSON_FILE = "settings.json"

def read_default_settings(item):
    with open("settings.json") as f:
        settings_json = json.load(f)
    return settings_json[item]

def save_default_settings(item, value):
    with open("settings.json") as f:
        settings_json = json.load(f)
    settings_json[item] = value
    # sleep 0.2s to secure close settings.json
    time.sleep(0.2)
    with open("settings.json", "w") as f:
        json.dump(settings_json, f)
