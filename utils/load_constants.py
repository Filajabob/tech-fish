import json


def load_constants():
    with open("assets/json/constants.json", 'r') as f:
        return json.load(f)