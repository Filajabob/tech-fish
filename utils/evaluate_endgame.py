import requests
import json

def evaluate_endgame(board):
    """Evaluates and returns a move for a position when there are 7 pieces or less."""

    if len(board.piece_map()) > 7:
        raise ValueError("Position has more than 7 pieces")

    r = requests.get(f"http://tablebase.lichess.ovh/standard?fen={board.fen().replace(' ', '_')}")

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

