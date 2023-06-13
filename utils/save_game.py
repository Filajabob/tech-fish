import datetime
import utils


def save_game(board):
    current_time = datetime.datetime.now()
    formatted_time = current_time.strftime("%m-%d-%Y-%H-%M-%S")

    with open(f"games/{formatted_time}.pgn", 'w', encoding="utf-8") as f:
        f.write(utils.generate_pgn(board))
