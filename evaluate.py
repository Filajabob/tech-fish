import chess
from chess import Termination
import random
import utils
import re
import time

constants = utils.load_constants()


def evaluate_position(board):
    """Evaluates the current material of a singular position."""
    # If the game has ended, figure out who is winning
    if board.outcome():
        outcome = board.outcome()

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

        # Evaluate king safety
        king_safety = 0

        if board.is_check():
            king_safety -= constants["king_safety"]

        # Give a bonus for pieces being on a central square
        central_squares = [
            chess.C3, chess.D3, chess.E3, chess.F3,
            chess.C4, chess.D4, chess.E4, chess.F4,
            chess.C5, chess.D5, chess.E5, chess.F5,
            chess.C6, chess.D6, chess.E6, chess.F6,
        ]

        # Central Score = Central Pieces Owned by Us - Central Pieces Owned by Opponent
        # TODO: Incentivize pieces closer to the center
        central_score = 0
        for square in central_squares:
            piece = board.piece_at(square)
            if piece is not None:
                if piece.color == board.turn:
                    if piece.piece_type == 1:
                        # We really like pawns in the center
                        central_score += constants["central_pawn_score"]

                    elif piece.piece_type in [5, 6]:
                        # We don't want important pieces in the center
                        # TODO: Allow important pieces in the center later in the game
                        central_score += constants["central_important_piece_score"]

                    central_score += constants["central_score"]
                elif piece.color != board.turn:
                    if piece.piece_type == 1:
                        central_score -= constants["central_pawn_score"]

                    elif piece.piece_type in [5, 6]:
                        central_score -= constants["central_important_piece_score"]

                    central_score -= constants["central_score"]

        # Penalize for repeating moves
        repeat_score = 0

        if len(board.move_stack) >= 3:
            prev_move = board.move_stack[-3]
            curr_move = board.move_stack[-1]

            repeat_score += constants["repeat_score"]

        # # Penalize for moving a piece twice in the opening
        # # TODO: Make this not so imbalanced
        opening_repeat_score = 0
        move_count = board.fullmove_number
        if move_count < 6:
            for move in board.move_stack:
                if not board.piece_at(move.from_square):
                    continue
                if board.piece_at(move.from_square).piece_type not in [chess.KING, chess.QUEEN]:
                    if board.is_capture(move) or move.promotion or move.from_square in central_squares:
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
        if board.move_stack[-1].drop == 1 and \
                chess.square_file(board.move_stack[-1].from_square) != chess.square_file(
                board.move_stack[-1].to_square):
            pawn_attack_score += constants["pawn_attack_score"]

        if board.turn:
            return material_balance + king_safety + central_score + repeat_score + pawn_attack_score + opening_repeat_score
        else:
            return material_balance - (king_safety + central_score + repeat_score + pawn_attack_score + opening_repeat_score)


def minimax(board, depth, alpha, beta, is_maximizing):
    if depth == 0:
        return evaluate_position(board), None

    if is_maximizing:
        max_score = float('-inf')
        best_move = None
        for move in board.legal_moves:
            board.push(move)
            score = minimax(board, depth - 1, alpha, beta, False)[0]
            board.pop()

            if score > max_score:
                max_score = score
                best_move = move

            alpha = max(alpha, max_score)
            if alpha >= beta:
                break

        return max_score, best_move

    else:
        min_score = float('inf')
        best_move = None

        for move in board.legal_moves:
            board.push(move)
            score = minimax(board, depth - 1, alpha, beta, True)[0]
            board.pop()

            if score < min_score:
                min_score = score
                best_move = move

            beta = min(beta, min_score)

            if beta <= alpha:
                break

        return min_score, best_move


def find_move(board, max_depth, time_limit, allow_book=True, engine_is_maximizing=False):
    # Check if we are in a book position
    opening_pgns = utils.load_openings()
    combined = '\t'.join(opening_pgns)
    board_pgn = utils.generate_pgn(board)

    if board_pgn in combined and allow_book:
        book = True
        continuations = []

        # We are in a book position, find a continuation
        for opening in opening_pgns:
            if opening.startswith(board_pgn):
                continuations.append(opening)

        if len(continuations) == 0:
            return find_move(board, max_depth, time_limit, False)

        continuation = random.choice(continuations)
        continuation = re.sub(f'^{board_pgn}', '', continuation)

        return {
            "move": continuation.split(' ')[0],
            "eval": "Book",
            "depth": None
        }

    start_time = time.time()
    best_move = None

    for depth in range(1, max_depth + 1):
        alpha = float('-inf')
        beta = float('inf')
        score, best_move = minimax(board, depth, alpha, beta, engine_is_maximizing)

        if time.time() - start_time > time_limit:
            break

    return {
        "move": str(best_move),
        "eval": score,
        "depth": depth
    }
