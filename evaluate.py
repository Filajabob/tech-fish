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
        material_balance = utils.material_balance(board)
        space = len(list(board.legal_moves))
        #space_value = space * utils.load_constants()["space_value"]

        #if board.turn == chess.BLACK:
        #    space_value = -space_value

        return material_balance


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


def find_move(board, max_depth, time_limit):
    board = chess.Board(board.fen())
    # Check if we are in a book position
    opening_pgns = utils.load_openings()
    combined = '\t'.join(opening_pgns)
    board_pgn = utils.generate_pgn(board)

    if board_pgn in combined and board_pgn == "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1":
        book = True
        continuations = []

        # We are in a book position, find a continuation
        for opening in opening_pgns:
            if opening.startswith(board_pgn):
                continuations.append(opening)

        continuation = random.choice(continuations)
        continuation = re.sub(f'^{board_pgn}', '', continuation)

        return {
            "move": continuation.split(' ')[0],
            "eval": "Book",
            "depth": None
        }
    else:
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
