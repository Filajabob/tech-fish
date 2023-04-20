from chess import Termination
import random
import utils


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


def find_move(board):
    # Check if we are in a book position
    opening_pgns = [opening["moves"] for opening in utils.load_openings().values()]

    board_pgn = utils.generate_pgn(board)

    if board_pgn in opening_pgns:
        # We are in a book position, load a random continuation
        continuations = []

        # Generate a list of all possible continuations
        for opening in opening_pgns:
            if opening.startswith(board_pgn):
                continuations.append(opening)




    # Find the "best move" for the current color
    return random.choice([str(legal_move) for legal_move in board.legal_moves])
