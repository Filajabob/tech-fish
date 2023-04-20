import requests
import json


def load_openings():
    openings = requests.get("https://raw.githubusercontent.com/hayatbiralem/eco.json/master/eco.json")

    return json.loads(openings)
