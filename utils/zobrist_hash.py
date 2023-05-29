import chess
import random
import json
import utils

constants = utils.load_constants()


class ZobristHash:
    def __init__(self, board):
        self.zobrist_array = {}
        self.en_passant_squares = [
            chess.A3, chess.B3, chess.C3, chess.D3, chess.E3, chess.F3, chess.G3, chess.H3,
            chess.A6, chess.B6, chess.C6, chess.D6, chess.E6, chess.F6, chess.G6, chess.H6
        ]
        self.en_passant = []

        for piece in chess.PIECE_TYPES:
            # Create a dict for each piece, ready to fill with squares
            self.zobrist_array[piece] = {}

        for piece in chess.PIECE_TYPES:
            for square in chess.SQUARES:
                # Fill piece dicts with square keys
                self.zobrist_array[piece][square] = random.getrandbits(64)

        for en_passant_square in self.en_passant_squares:
            self.en_passant.append(random.getrandbits(64))

        self.current_hash = 0

        for square, piece in board.piece_map().items():
            self.current_hash ^= self.zobrist_array[piece.piece_type][square]

        if board.ep_square is not None:
            self.current_hash ^= self.en_passant[chess.square_file(board.ep_square)]

        self.zobrist_array[-1] = random.getrandbits(64)

    def move(self, move, board):
        if not move:
            # Null move, switch turn
            if not board.turn:
                # Update the hash to include who's turn it is
                self.current_hash ^= self.zobrist_array["-1"]

            return self.current_hash

        # Call Zobrist Hashing before the actual push
        piece = board.piece_type_at(move.from_square)

        # XOR out the piece from its origin square
        try:
            self.current_hash ^= self.zobrist_array[piece][move.from_square]
        except Exception as e:
            print(board)
            print(move)
            raise e

        if board.is_capture(move):
            if board.is_en_passant(move):
                # XOR the en passant
                self.current_hash ^= self.en_passant[self.en_passant_squares.index(move.to_square)]

            else:
                captured_piece = board.piece_type_at(move.to_square)

                # XOR out the captured piece, if any
                self.current_hash ^= self.zobrist_array[captured_piece][move.to_square]
        if move.promotion:
            # XOR out the pawn that promoted, if any
            self.current_hash ^= self.zobrist_array[piece][move.to_square]

            # XOR in the newly promoted piece
            self.current_hash ^= self.zobrist_array[move.promotion][move.to_square]
        else:
            # Nothing special, XOR in the piece to its new square
            self.current_hash ^= self.zobrist_array[piece][move.to_square]

        # Castling logic
        if board.is_castling(move):
            if move.to_square == chess.G1:
                self.current_hash ^= self.zobrist_array[chess.ROOK][chess.H1]
                self.current_hash ^= self.zobrist_array[chess.ROOK][chess.F1]
            elif move.to_square == chess.C1:
                self.current_hash ^= self.zobrist_array[chess.ROOK][chess.A1]
                self.current_hash ^= self.zobrist_array[chess.ROOK][chess.D1]
            elif move.to_square == chess.G8:
                self.current_hash ^= self.zobrist_array[chess.ROOK][chess.H8]
                self.current_hash ^= self.zobrist_array[chess.ROOK][chess.F8]
            elif move.to_square == chess.C8:
                self.current_hash ^= self.zobrist_array[chess.ROOK][chess.A8]
                self.current_hash ^= self.zobrist_array[chess.ROOK][chess.D8]

        if not board.turn:
            # Update the hash to include who's turn it is
            self.current_hash ^= self.zobrist_array[-1]

        return self.current_hash

    def pop(self, move, board):
        return self.move(move, board)



