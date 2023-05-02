import requests
import json
from errors import *


def evaluate_endgame(board):
    """Evaluates and returns a move for a position when there are 7 pieces or less."""

    if len(board.piece_map()) > 7:
        raise ValueError("Position has more than 7 pieces")

    r = requests.get(f"http://tablebase.lichess.ovh/standard?fen={board.fen().replace(' ', '_')}")

    if not r.ok:
        # For some reason, tablebase lookup didn't work
        raise TablebaseLookupError(f"tablebase.lichess.ovh returned a status of {r.status_code}; lookup failed")

    try:
        tablebase_eval = json.loads(r.content)
    except json.decoder.JSONDecodeError:
        raise Exception(r.content)

    move = tablebase_eval["moves"][0]["san"]

    if tablebase_eval["dtm"]:
        eval = f"M{tablebase_eval['dtm'] // 2}"
    else:
        if tablebase_eval["category"] == "draw":
            eval = "Draw"
        else:

            if board.turn:
                ref_color = "white"
            else:
                ref_color = "black"

            eval = f"{tablebase_eval['category'].title()} for {ref_color}"


    return {
        "move": move,
        "eval": eval
    }

