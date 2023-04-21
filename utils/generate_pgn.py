import chess
import utils


def generate_san_move_list(board):
    _board = chess.Board(fen=utils.load_constants()["starting_fen"])
    moves = board.move_stack

    pgn = []

    for move in moves:
        pgn.append(_board.san(move) + ' ')
        _board.push_san(str(move))

    return pgn


def generate_pgn(board):
    """Returns unnumbered PGN"""

    _board = chess.Board(fen=utils.load_constants()["starting_fen"])
    moves = board.move_stack

    pgn = ""

    for move in moves:
        pgn += _board.san(move) + ' '
        _board.push_san(str(move))

    return pgn


