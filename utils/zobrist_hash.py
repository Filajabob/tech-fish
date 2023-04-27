import chess
import random


class ZobristHash:
    def __init__(self, board):
        self.zobrist_array = {}

        for piece in chess.PIECE_TYPES:
            self.zobrist_array[piece] = {}

        for piece in chess.PIECE_TYPES:
            for square in chess.SQUARES:
                self.zobrist_array[piece][square] = random.getrandbits(64)

        self.en_passant = [random.getrandbits(64) for _ in range(8)]
        self.turn = random.getrandbits(64)

        self.current_hash = 0

        for square, piece in board.piece_map().items():
            self.current_hash ^= self.zobrist_array[piece.piece_type][square]

        if board.ep_square is not None:
            self.current_hash ^= self.en_passant[chess.square_file(board.ep_square)]

        self.zobrist_array[-1] = random.getrandbits(64)

    def move(self, move, board):
        # Call Zobrist Hashing before the actual push
        piece = board.piece_type_at(move.from_square)

        # XOR out the piece from its origin square
        self.current_hash ^= self.zobrist_array[piece][move.from_square]

        if board.is_capture(move):
            if board.is_en_passant(move):
                # XOR out the en-passanted pawn
                if self.turn == chess.BLACK:
                    self.current_hash ^= self.zobrist_array[1][move.to_square - 8]
                else:
                    self.current_hash ^= self.zobrist_array[1][move.to_square + 8]

                # XOR in the pawn to its new square
                self.current_hash ^= self.zobrist_array[piece][move.to_square]

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

        self.current_hash ^= self.zobrist_array[-1]

        return self.current_hash

    def pop(self, move, board):
        return self.move(move, board)



