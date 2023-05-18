import chess
from .load_constants import load_constants
from .get_piece_value import get_piece_value
from .see import see, see_capture

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

        see_score = see_capture(move, board)

        if see_score:
            score += see_score

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


def order_moves(board, moves, transposition_table, hash, depth, killer_moves, best_move=None):
    scored_moves = []

    killer_moves = killer_moves[board.turn][depth]
    killer_moves = [*set(killer_moves)]  # Remove duplicates

    for move in moves:
        scored_moves.append((move, score_move(move, board, transposition_table, hash)))

    sorted_scored_moves = sorted(scored_moves, key=lambda x: x[1], reverse=True)
    scored_moves = [move[0] for move in sorted_scored_moves]

    # Ensure the scored moves and killer moves don't have a duplicate of the best move
    scored_moves = [move for move in scored_moves if move != best_move]

    if best_move is not None:
        scored_moves.insert(0, best_move)  # Insert the best move at the beginning

    # Ensure there is no overlap between killer moves and regular moves
    scored_moves = [move for move in scored_moves if move not in killer_moves]

    return scored_moves
