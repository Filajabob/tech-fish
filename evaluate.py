import chess
from chess import Termination
import random
import utils
import re
import time


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
        # Evaluate material
        material_balance = utils.material_balance(board)

        # Evaluate "move freedom"
        moves = list(board.legal_moves)
        move_freedom = 0

        for move in moves:
            if move.drop in [2, 3, 4, 5]:
                # A knight, bishop, or rook being able to move is probably a good thing, so we incentivize this
                if board.turn: move_freedom += move.drop * 0.01
                if not board.turn: move_freedom -= move.drop * 0.01

                # We see what the opponent can do, if they also have freedom, we decentivize this
                board.push(move)

                rmoves = list(board.legal_moves)
                for rmove in rmoves:
                    if rmove.drop in [2, 3, 4, 5]:
                        if board.turn: move_freedom -= move.drop * 0.25
                        if not board.turn: move_freedom += move.drop * 0.25

                board.pop()

        # Evaluate king safety
        king_safety = 0

        if board.is_check():
            if board.turn: king_safety -= 0.5
            if not board.turn: king_safety += 0.5

        # Give a bonus for pieces being on a central square
        central_squares = [
            chess.C3, chess.D3, chess.E3, chess.F3,
            chess.C4, chess.D4, chess.E4, chess.F4,
            chess.C5, chess.D5, chess.E5, chess.F5,
            chess.C6, chess.D6, chess.E6, chess.F6,
        ]

        central_score = 0
        for square in central_squares:
            piece = board.piece_at(square)
            if piece is not None and piece.color:
                central_score += 2
            if piece is not None and not piece.color:
                central_score -= 2

        # Penalize for repeating moves
        repeat_score = 0
        if len(board.move_stack) >= 3:
            prev_move = board.move_stack[-3]
            curr_move = board.move_stack[-1]

            if prev_move.from_square == curr_move.to_square and board.turn:
                penalty_score = -2.5
            if prev_move.from_square == curr_move.to_square and not board.turn:
                penalty_score = 2.5

        return material_balance + move_freedom + king_safety + central_score + repeat_score


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


def find_move(board, max_depth, time_limit, allow_book=True):
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
        score, best_move = minimax(board, depth, alpha, beta, True)

        if time.time() - start_time > time_limit:
            break

    return {
        "move": str(best_move),
        "eval": score,
        "depth": depth
    }
