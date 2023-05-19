import chess
from .get_piece_value import get_piece_value


def get_lowest_valued_piece_square(board, squares):
    lowest_value = float('inf')
    lowest_square = None

    for square in squares:
        piece_value = get_piece_value(board.piece_at(square))
        if piece_value < lowest_value:
            lowest_value = piece_value
            lowest_square = square

    return lowest_square


def see(board, square):
    value = 0
    piece = get_lowest_valued_piece_square(board, board.attackers(board.turn, square))

    if piece:
        captured_piece = board.piece_at(square)

        if not captured_piece: return 0  # TODO: Support en passant

        board.push(chess.Move(piece, square))
        value = max(0, get_piece_value(captured_piece) - see(board, square))
        board.pop()

    return value


def see_capture(move, board):
    value = 0

    captured_piece = board.piece_at(move.to_square)

    if captured_piece is None:
        return

    board.push(move)
    value = get_piece_value(captured_piece) - see(board, move.to_square)
    board.pop()

    return value
