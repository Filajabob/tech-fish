from .load_constants import load_constants
from .get_piece_value import get_piece_value

constants = load_constants()


def score_move(move, board, transposition_table, hash):
    if board.is_capture(move):
        # Use MVV-LVA

        aggressor = board.piece_at(move.from_square)
        victim = board.piece_at(move.to_square)
        score = get_piece_value(aggressor) - get_piece_value(victim)

        return score
    else:
        # Use TT ordering
        if transposition_table.entry_exists(hash.current_hash):
            entry = transposition_table.get_entry(hash.current_hash)
            return abs(entry["score"])
        else:
            return 0


def order_moves(board, moves, transposition_table, hash):
    """
    Uses Most Valuable Victim - Least Valuable Aggressor, and TT move ordering
    """

    scored_moves = []

    for move in moves:
        scored_moves.append((move, score_move(move, board, transposition_table, hash)))

    sorted_scored_moves = sorted(scored_moves, key=lambda x: x[1], reverse=True)
    scored_moves = [move[0] for move in scored_moves]

    return scored_moves
