import requests
import json

def evaluate_endgame(board):
    """Evaluates and returns a move for a position when there are 7 pieces or less."""

    if len(board.piece_map()) > 7:
        raise ValueError("Position has more than 7 pieces")

    r = requests.get(f"http://tablebase.lichess.ovh/standard?fen={board.fen().replace(' ', '_')}")
    json_r = json.loads(r.content)

    move = json_r["moves"][0]  # Load the best move

    # TODO: Make eval proper

    if move["dtm"]:
        eval = f"M{(-move['dtm']) - 1}"
    if move["checkmate"]:
        eval = "M0"
    else:
        eval = f"DTZ{move['dtz']}"


    return {
        "move": move["san"],
        "eval": eval
    }

