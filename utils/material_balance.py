# https://github.com/niklasf/python-chess/discussions/864#discussioncomment-2351174

import chess
from .load_constants import load_constants

constants = load_constants()
piece_values = constants["piece_values"]


def material_balance(board):
    white = board.occupied_co[chess.WHITE]
    black = board.occupied_co[chess.BLACK]

    return (
        piece_values["1"] * chess.popcount(white & board.pawns) - chess.popcount(black & board.pawns) +
        piece_values["2"] * (chess.popcount(white & board.knights) - chess.popcount(black & board.knights)) +
        piece_values["3"] * (chess.popcount(white & board.bishops) - chess.popcount(black & board.bishops)) +
        piece_values["4"] * (chess.popcount(white & board.rooks) - chess.popcount(black & board.rooks)) +
        piece_values["5"] * (chess.popcount(white & board.queens) - chess.popcount(black & board.queens))
    )