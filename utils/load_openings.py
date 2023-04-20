import requests
import json


def load_openings():
    with open("assets/json/games.txt", 'r') as f:
        return f.read().split('\n')
