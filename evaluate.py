from chess import Termination
import random
import utils
import re


def evaluate_material(board):
    """Evaluates the current material of a singular position."""

    # If the game has ended, figure out who is winning
    if board.outcome():
        termination = board.outcome()

        if termination.termination == Termination.CHECKMATE:
            if termination.winner:
                # White won due to checkmate
                return float("inf")
            if not termination.winner:
                # Black won due to checkmate
                return -float("inf")

        if 7 >= termination >= 2:
            # Game ended due to draw
            return 0

    else:
        return utils.material_balance(board)


def minimax(board, depth, is_maximizing):
    if depth == 0:
        return evaluate_material(board), None

    if is_maximizing:
        max_score = float('-inf')
        best_move = None
        for move in board.legal_moves:
            board.push(move)
            score = minimax(board, depth - 1, False)[0]
            board.pop()

            if score > max_score:
                max_score = score
                best_move = move

        return max_score, best_move

    else:
        min_score = float('inf')
        best_move = None

        for move in board.legal_moves:
            board.push(move)
            score = minimax(board, depth - 1, True)[0]
            board.pop()

            if score < min_score:
                min_score = score
                best_move = move

        return min_score, best_move


def find_move(board):
    # Check if we are in a book position
    opening_pgns = utils.load_openings()
    combined = '\t'.join(opening_pgns)
    board_pgn = utils.generate_pgn(board)

    book = False

    if board_pgn in combined:
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
            "eval": 0
        }
    else:
        eval = minimax(board, 2, False)

        return {
            "move": str(eval[1]),
            "eval": eval[0]
        }
