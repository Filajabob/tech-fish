import chess
import random


zobrist_pieces = {}
for piece_type in range(1, 7):
    for color in range(2):
        for square in range(64):
            zobrist_pieces[(piece_type, color, square)] = random.getrandbits(64)


def zobrist_hash(board):
    h = 0
    for square, piece in board.piece_map().items():
        piece_type = piece.piece_type
        color = piece.color
        h ^= zobrist_pieces[(piece_type, color, square)]
    if board.turn == chess.BLACK:
        h ^= zobrist_pieces[(-1, -1, -1)]  # XOR with random number for black to move
    return h
