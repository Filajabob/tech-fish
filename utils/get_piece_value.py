from .load_constants import load_constants

constants = load_constants()


def get_piece_value(piece):
    if piece is None:
        return

    return constants["piece_values"][str(piece.piece_type)]