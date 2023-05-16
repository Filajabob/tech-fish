import chess
import random
import json
import utils

constants = utils.load_constants()


class ZobristHash:
    def __init__(self, board):
        with open(constants["zobrist_keys_filepath"], 'r+') as f:
            self.zobrist_array = json.load(f)

        self.en_passant_squares = [
            chess.A3, chess.B3, chess.C3, chess.D3, chess.E3, chess.F3, chess.G3, chess.H3,
            chess.A6, chess.B6, chess.C6, chess.D6, chess.E6, chess.F6, chess.G6, chess.H6
        ]
        self.current_hash = 0

        for square, piece in board.piece_map().items():
            self.current_hash ^= self.zobrist_array[str(piece.piece_type)][str(square)]

        if board.ep_square is not None:
            self.current_hash ^= self.zobrist_array["en_passant"][chess.square_file(board.ep_square)]

    def generate_new_keys(self, board):
        self.zobrist_array = {}
        self.en_passant_squares = [
            chess.A3, chess.B3, chess.C3, chess.D3, chess.E3, chess.F3, chess.G3, chess.H3,
            chess.A6, chess.B6, chess.C6, chess.D6, chess.E6, chess.F6, chess.G6, chess.H6
        ]

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
            self.current_hash ^= self.zobrist_array["en_passant"][chess.square_file(board.ep_square)]

        self.zobrist_array[-1] = random.getrandbits(64)

    def move(self, move, board):
        if not move:
            # Move is null, switch the turn
            if not board.turn:
                # Update the hash to include who's turn it is
                self.current_hash ^= self.zobrist_array["-1"]

            return self.current_hash

        # Call Zobrist Hashing before the actual push
        piece = board.piece_type_at(move.from_square)

        # XOR out the piece from its origin square
        self.current_hash ^= self.zobrist_array[str(piece)][str(move.from_square)]

        if board.is_capture(move):
            if board.is_en_passant(move):
                # XOR the en passant
                self.current_hash ^= self.zobrist_array["en_passant"][self.en_passant_squares.index(move.to_square)]

            else:
                captured_piece = board.piece_type_at(move.to_square)

                # XOR out the captured piece, if any
                self.current_hash ^= self.zobrist_array[str(captured_piece)][str(move.to_square)]
        if move.promotion:
            # XOR out the pawn that promoted, if any
            self.current_hash ^= self.zobrist_array[str(piece)][str(move.to_square)]

            # XOR in the newly promoted piece
            self.current_hash ^= self.zobrist_array[str(move.promotion)][str(move.to_square)]
        else:
            # Nothing special, XOR in the piece to its new square
            self.current_hash ^= self.zobrist_array[str(piece)][str(move.to_square)]

        # Castling logic
        if board.is_castling(move):
            if move.to_square == chess.G1:
                self.current_hash ^= self.zobrist_array[str(chess.ROOK)][str(chess.H1)]
                self.current_hash ^= self.zobrist_array[str(chess.ROOK)][str(chess.F1)]
            elif move.to_square == chess.C1:
                self.current_hash ^= self.zobrist_array[str(chess.ROOK)][str(chess.A1)]
                self.current_hash ^= self.zobrist_array[str(chess.ROOK)][str(chess.D1)]
            elif move.to_square == chess.G8:
                self.current_hash ^= self.zobrist_array[str(chess.ROOK)][str(chess.H8)]
                self.current_hash ^= self.zobrist_array[str(chess.ROOK)][str(chess.F8)]
            elif move.to_square == chess.C8:
                self.current_hash ^= self.zobrist_array[str(chess.ROOK)][str(chess.A8)]
                self.current_hash ^= self.zobrist_array[str(chess.ROOK)][str(chess.D8)]

        if not board.turn:
            # Update the hash to include who's turn it is
            self.current_hash ^= self.zobrist_array["-1"]

        return self.current_hash

    def pop(self, move, board):
        return self.move(move, board)



