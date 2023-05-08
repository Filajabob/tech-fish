import chess
import utils

constants = utils.load_constants()

outer_central_squares = [
        chess.C3, chess.D3, chess.E3, chess.F3,
        chess.C4,                     chess.F4,
        chess.C5,                     chess.F5,
        chess.C6, chess.D6, chess.E6, chess.F6,
]

very_central_squares = [
        chess.D4, chess.E4,
        chess.D5, chess.E5,
]


def evaluate_position(board):
    """Evaluates the current material of a singular position."""
    # If the game has ended, figure out who is winning
    outcome = board.outcome()
    if outcome:
        if outcome.result() in ["1-0", "0-1", "1/2-1/2"]:
            if outcome.result() == "1-0":
                return float("inf")
            elif outcome.result() == "0-1":
                return float("-inf")
            elif outcome.result() == "1/2-1/2":
                return 0

    else:
        # Evaluate material (positive is good for white, negative good for black)
        material_balance = utils.material_balance(board)

        # Give a bonus for pieces being on a central square

        # Central Score = Central Pieces Owned by Us - Central Pieces Owned by Opponent
        # TODO: Incentivize pieces closer to the center
        central_score = 0
        for square in outer_central_squares:
            piece = board.piece_at(square)
            if piece is not None:
                if piece.color == board.turn:
                    if piece.piece_type == 1:
                        # We really like pawns in the center
                        central_score += constants["central_pawn_score"]

                    central_score += constants["central_score"]
                elif piece.color != board.turn:
                    if piece.piece_type == 1:
                        central_score -= constants["central_pawn_score"]

                    elif piece.piece_type in [5, 6]:
                        central_score -= constants["central_important_piece_score"]

                    central_score -= constants["central_score"]

        for square in very_central_squares:
            piece = board.piece_at(square)
            if piece is not None:
                if piece.color == board.turn:
                    if piece.piece_type == 1:
                        # We really like pawns in the center
                        central_score += constants["central_pawn_score"] * 1.5

                    central_score += constants["central_score"]
                elif piece.color != board.turn:
                    if piece.piece_type == 1:
                        central_score -= constants["central_pawn_score"]

                    elif piece.piece_type in [5, 6]:
                        central_score -= constants["central_important_piece_score"]

                    central_score -= constants["central_score"] * 1.5

        king_safety_score = 0

        # If there are many possible checks on the next move, the other side doesn't have good king safety
        for legal_move in board.legal_moves:
            if board.gives_check(legal_move):
                king_safety_score -= constants["king_safety"]

        # Penalize for repeating moves
        repeat_score = 0

        if len(board.move_stack) >= 3:
            if board.move_stack[-3] == board.move_stack[-1]:
                repeat_score += constants["repeat_score"]

        # # Penalize for moving a piece twice in the opening
        opening_repeat_score = 0
        move_count = board.fullmove_number
        if move_count < 10:
            for move in board.move_stack:
                if not board.piece_at(move.from_square):
                    continue
                if board.piece_at(move.from_square).piece_type not in [chess.KING, chess.QUEEN]:
                    if board.is_capture(move) or move.promotion or move.from_square in outer_central_squares + \
                            very_central_squares:
                        continue
                    if move_count < 4:
                        if move_count == 2 and board.piece_at(move.from_square).color == chess.WHITE:
                            continue
                        if move_count == 3 and board.piece_at(move.from_square).color == chess.BLACK:
                            continue

                    opening_repeat_score += constants["opening_repeat_score"]

        # Incentivize pawn attacks
        pawn_attack_score = 0

        # This means a pawn has taken something in the previous move, which is probably bad for us
        prev_move = board.move_stack[-1]
        if prev_move.drop == 1 and \
                chess.square_file(prev_move.from_square) != chess.square_file(
                prev_move.to_square):
            pawn_attack_score -= constants["pawn_attack_score"]

        if board.turn:
            return material_balance + central_score + repeat_score + pawn_attack_score + opening_repeat_score + \
                   king_safety_score
        else:
            return material_balance - (central_score + repeat_score + pawn_attack_score + opening_repeat_score +
                                       king_safety_score)
