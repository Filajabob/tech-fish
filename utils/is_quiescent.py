from .material_balance import material_balance
from .see import see


def has_forcing_moves(board):
    # TODO: Make better
    for move in [move for move in board.legal_moves if board.is_capture(move)]:
        if see(board, move.to_square) >= 0:
            return True

    return False


def is_quiescent(board):
    return not board.is_check() and material_balance(board) != 0 and not has_forcing_moves(board)
