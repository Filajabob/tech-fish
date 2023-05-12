from .material_balance import material_balance


def has_forcing_moves(board):
    for move in board.legal_moves:
        if board.is_capture(move) or board.gives_check(move):
            return True

    return False


def is_quiescent(board):
    return board.is_check() or material_balance(board) != 0 or has_forcing_moves(board)
