import chess
from .load_constants import load_constants
from .get_piece_value import get_piece_value

constants = load_constants()


def score_move(move, board, transposition_table, hash):
    if board.is_capture(move):
        # Use MVV-LVA

        aggressor = board.piece_at(move.from_square)

        if not board.is_en_passant(move):
            victim = board.piece_at(move.to_square)
        else:
            victim = chess.Piece(piece_type=1, color=not board.turn)

        score = get_piece_value(aggressor) - get_piece_value(victim)

        return score
    else:
        # Use TT ordering
        if transposition_table.entry_exists(hash.current_hash):
            entry = transposition_table.get_entry(hash.current_hash)

            if board.turn:
                # White to move. Positive is good for white, negative is bad
                return entry["score"]
            else:
                return -entry["score"]
        else:
            return 0


def order_moves(board, moves, transposition_table, hash, killer_moves=None, best_move=None):
    """
    Uses Most Valuable Victim - Least Valuable Aggressor, and TT move ordering

    Killer moves not implemented yet.
    """

    scored_moves = []

    for move in moves:
        scored_moves.append((move, score_move(move, board, transposition_table, hash)))

    sorted_scored_moves = sorted(scored_moves, key=lambda x: x[1], reverse=True)
    scored_moves = [move[0] for move in sorted_scored_moves]

    if best_move is None:
        return scored_moves

    if best_move in scored_moves:
        scored_moves.remove(best_move)

    return [best_move] + scored_moves
