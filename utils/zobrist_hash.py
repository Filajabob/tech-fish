import chess
import random


class ZobristHash:
    def __init__(self):
        self.pieces = {}

        for piece in chess.PIECE_TYPES:
            for square in chess.SQUARES:
                self.pieces[(piece, square)] = random.getrandbits(64)

        self.en_passant = [random.getrandbits(64) for _ in range(8)]
        self.turn = random.getrandbits(64)

    def __call__(self, board: chess.Board) -> int:
        h = 0

        for square, piece in board.piece_map().items():
            h ^= self.pieces[(piece.piece_type, square)]

        if board.ep_square is not None:
            h ^= self.en_passant[chess.square_file(board.ep_square)]

        if board.turn == chess.BLACK:
            h ^= self.turn

        return h
