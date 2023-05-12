from .material_balance import material_balance


def has_forcing_moves(board):
    # TODO: Make better
    for move in board.legal_moves:
        if board.is_capture(move) or board.gives_check(move):
            return True

    return False


def is_quiescent(board):
    return not board.is_check() and material_balance(board) != 0 and not has_forcing_moves(board)
