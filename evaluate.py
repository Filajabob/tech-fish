import chess
from chess import Termination
import random
import utils
import re
import time
from errors import *
import psutil

constants = utils.load_constants()
zobrist_hash = utils.ZobristHash()
positions_evaluated = 0

# TODO: Fix Zobrist hashing taking too long, or remove it

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
            prev_move = board.move_stack[-3]
            curr_move = board.move_stack[-1]

            repeat_score += constants["repeat_score"]

        # # Penalize for moving a piece twice in the opening
        # # TODO: Make this not so imbalanced
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
        if board.move_stack[-1].drop == 1 and \
                chess.square_file(board.move_stack[-1].from_square) != chess.square_file(
                board.move_stack[-1].to_square):
            pawn_attack_score -= constants["pawn_attack_score"]

        global positions_evaluated
        positions_evaluated += 1

        if board.turn:
            return material_balance + central_score + repeat_score + pawn_attack_score + opening_repeat_score + \
                   king_safety_score
        else:
            return material_balance - (central_score + repeat_score + pawn_attack_score + opening_repeat_score +
                                       king_safety_score)


transposition_table = {}


def minimax(board, depth, alpha, beta, is_maximizing):
    """
    A minimax evaluation function, which uses alpha-beta pruning and Zobrist hashing.
    :param board:
    :param depth:
    :param alpha:
    :param beta:
    :param is_maximizing:
    :return:
    """

    # Calculate this board's Zobrist hash
    hash_key = zobrist_hash(board)

    # Check if there is an entry in the transposition table for this hash
    if hash_key in transposition_table:
        entry = transposition_table[hash_key]
        if entry['depth'] >= depth:
            if entry['type'] == 'exact':
                return entry
            elif entry['type'] == 'lowerbound':
                alpha = max(alpha, entry['score'])
            elif entry['type'] == 'upperbound':
                beta = min(beta, entry['score'])
            if alpha >= beta:
                return entry

    # If we reached the bottom of the tree, evaluate the position
    if depth == 0:
        transposition_table[hash_key] = {
            "score": evaluate_position(board),
            "best_move": None,
            "depth": depth,
            "type": "exact"
        }

        return {
            "score": evaluate_position(board),
            "best_move": None,
            "depth": depth
        }

    if is_maximizing:
        # Find best move for the maximizing player (white)
        max_score = float('-inf')
        best_move = None
        for move in sorted(board.legal_moves, key=lambda move: utils.capture_value(board, move), reverse=True):
            board.push(move)
            score = minimax(board, depth - 1, alpha, beta, False)["score"]
            board.pop()

            if score > max_score:
                max_score = score
                best_move = move

            alpha = max(alpha, max_score)

            if alpha >= beta:
                break

        transposition_table[hash_key] = {
            'score': max_score,
            'best_move': best_move,
            'depth': depth,
            "type": "lowerbound"
        }

        return {
            'score': max_score,
            'best_move': best_move,
            'depth': depth
        }

    else:
        # Find best move for minimizing player (black)
        min_score = float('inf')
        best_move = None

        for move in sorted(board.legal_moves, key=lambda move: utils.capture_value(board, move)):
            board.push(move)
            score = minimax(board, depth - 1, alpha, beta, True)["score"]
            board.pop()

            if score < min_score:
                min_score = score
                best_move = move

            beta = min(beta, min_score)

            if beta <= alpha:
                break

        transposition_table[hash_key] = {
            'score': min_score,
            'best_move': best_move,
            'depth': depth,
            "type": "upperbound"
        }


        return {
            'score': min_score,
            'best_move': best_move,
            'depth': depth
        }


def find_move(board, max_depth, time_limit, *, allow_book=True, engine_is_maximizing=False):
    # Check if we are in an endgame
    if len(board.piece_map()) <= 7:
        try:
            tablebase_result = utils.evaluate_endgame(board)

            return {
                "eval": tablebase_result["eval"],
                "move": tablebase_result["move"],
                "depth": None
            }

        except TablebaseLookupError:
            print("WARNING: Cannot connect to lichess.ovh for tablebase lookup. Ensure internet connection is stable.")

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
            return find_move(board, max_depth, time_limit, allow_book=False, engine_is_maximizing=engine_is_maximizing)

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
        search = minimax(board, depth, alpha, beta, engine_is_maximizing)

        # Don't break if a move wasn't found yet
        if time.time() - start_time > time_limit and best_move:
            break

    # Check if the transposition cache is too full, clear if necessary
    total_memory = psutil.virtual_memory().total
    python_memory = psutil.Process().memory_info().rss

    if python_memory / total_memory > utils.load_constants()["maximum_python_ram_percentage"]:
        # Too much RAM used, let's clear the cache
        global transposition_table
        transposition_table = {}

    return {
        "move": str(search["best_move"]),
        "eval": search["score"],
        "depth": depth
    }
