import random
import time
import re
import threading
import copy

import chess

import utils
from errors import *
from transposition_table import TranspositionTable
from evaluate_position import evaluate_position
from quiescence_search import quiescence_search

constants = utils.load_constants()
transposition_table = TranspositionTable()

zobrist_hash = utils.ZobristHash(chess.Board(constants["starting_fen"]))

abort_flag = threading.Event()

killer_moves = {
    chess.WHITE: [[] for _ in range(30)],
    chess.BLACK: [[] for _ in range(30)]
}


def minimax(board, depth, alpha, beta, is_maximizing, hash=zobrist_hash, first_move=None, allow_null=True):
    """
    A minimax evaluation function, which uses alpha-beta pruning, move ordering, and Zobrist hashing. Also uses Lazy SMP.
    :param allow_null: Allow null pruning?
    :param first_move: The current best move from the previous iterative deepening search, will be evaluated first
    :param hash:
    :param board:
    :param depth:
    :param alpha:
    :param beta:
    :param is_maximizing:
    :return:
    """

    hash_key = hash.current_hash

    # Check if there is an entry in the transposition table for this hash
    if transposition_table.entry_exists(hash_key):
        entry = transposition_table.get_entry(hash_key)
        if entry["depth"] >= depth:
            if entry["type"] == 'exact':
                return entry
            elif entry["type"] == "upperbound" and entry["score"] <= alpha:
                return entry
            elif entry["type"] == "lowerbound" and entry["score"] >= beta:
                return entry

        # Node needs to be examined, we can make it more efficient
        if not first_move:
            first_move = entry["best_move"]

    # If we reached the bottom of the tree, or if position is quiet, start quiescent search
    if depth == 0 or board.is_game_over():
        if not utils.is_quiescent(board):
            score = quiescence_search(board, alpha, beta)
        else:
            score = evaluate_position(board)

        if alpha < score < beta:
            type = "exact"
        elif score <= alpha:
            type = "upperbound"
        elif score >= beta:
            type = "lowerbound"
        else:
            type = None

        transposition_table.add_entry(hash_key, {
            "score": score,
            "best_move": None,
            "depth": depth,
            "type": type
        })

        return {
            "score": evaluate_position(board),
            "best_move": chess.Move.null(),
            "depth": depth
        }

    # Futility pruning
    if depth == 1:
        if not evaluate_position(board) + constants["piece_values"]["2"] > alpha and not board.is_check() \
                and not utils.is_generator_empty(board.legal_moves):
            # Unlikely to raise alpha, search captures and checks
            moves = [move for move in board.legal_moves if board.is_capture(move) or board.gives_check(move)]

        elif utils.is_generator_empty(board.legal_moves):
            return {
                "score": alpha,
                "best_move": None,
                "depth": depth
            }
        else:
            moves = board.legal_moves
    elif depth == 2:
        if not evaluate_position(board) + constants["piece_values"]["4"] > alpha and not board.is_check() \
                and not utils.is_generator_empty(board.legal_moves):
            # Unlikely to raise alpha, search captures and checks
            moves = [move for move in board.legal_moves if board.is_capture(move) or board.gives_check(move)]

        elif utils.is_generator_empty(board.legal_moves):
            return {
                "score": alpha,
                "best_move": None,
                "depth": depth
            }
        else:
            moves = board.legal_moves

    else:
        moves = board.legal_moves

    ordered_moves = utils.order_moves(board, moves, transposition_table, hash, depth, killer_moves, first_move)

    if is_maximizing:
        # Find best move for the maximizing player (white)
        max_score = float('-inf')  # Currently, the best score that can be achieved
        best_move = None  # The best move

        for i, move in enumerate(ordered_moves):
            ext = utils.extension(board, move)
            hash.move(move, board)  # Make sure the Zobrist Hash calculation happens before the move
            board.push(move)  # Try the move

            if i > constants["lmr_sample"] - 1 and not board.is_capture(move) and not board.gives_check(move) and \
                    not board.is_check() and depth - 1 - constants["lmr_reduction"] > 0:
                search = minimax(board, depth + ext - 1 - constants["lmr_reduction"], alpha, beta, not is_maximizing, hash)
            else:
                search = minimax(board, depth + ext - 1, alpha, beta, not is_maximizing, hash)

            board.pop()
            zobrist_hash.pop(move, board)

            score = search["score"]

            if score > max_score:
                max_score = score
                best_move = move

            alpha = max(alpha, max_score)

            if score > alpha:
                killer_moves[board.turn][depth].append(move)

            # fail high (beta cutoff)
            if alpha >= beta:
                break

        if alpha < max_score < beta:
            type = "exact"
        elif max_score <= alpha:
            type = "upperbound"
        elif max_score >= beta:
            type = "lowerbound"
        else:
            type = None

        transposition_table.add_entry(hash_key, {
            'score': max_score,
            'best_move': best_move,
            'depth': depth,
            "type": type
        })

        utils.kill_helpers(abort_flag)

        return {
            'score': max_score,
            'best_move': best_move,
            'depth': depth
        }

    else:
        # Find best move for minimizing player (black)
        min_score = float('inf')
        best_move = None

        for i, move in enumerate(ordered_moves):
            ext = utils.extension(board, move)
            hash.move(move, board)  # Make sure the Zobrist Hash calculation happens before the move
            board.push(move)

            if i > constants["lmr_sample"] - 1 and not board.is_capture(move) and not board.gives_check(move) and \
                    not board.is_check() and depth - 1 - constants["lmr_reduction"] > 0:
                search = minimax(board, depth + ext - 1 - constants["lmr_reduction"], alpha, beta, not is_maximizing, hash)
            else:
                search = minimax(board, depth + ext - 1, alpha, beta, not is_maximizing, hash)

            board.pop()
            zobrist_hash.pop(move, board)

            score = search["score"]

            if score < min_score:
                min_score = score
                best_move = move

            beta = min(beta, min_score)

            if score < beta:
                killer_moves[board.turn][depth].append(move)

            # fail high (beta cutoff)
            if alpha >= beta:
                break

        if alpha < min_score < beta:
            type = "exact"
        elif min_score <= alpha:
            type = "upperbound"
        elif min_score >= beta:
            type = "lowerbound"
        else:
            type = None

        transposition_table.add_entry(hash_key, {
            'score': min_score,
            'best_move': best_move,
            'depth': depth,
            "type": type
        })

        utils.kill_helpers(abort_flag)

        return {
            'score': min_score,
            'best_move': best_move,
            'depth': depth
        }


def find_move(board, max_depth, time_limit, *, allow_book=True, engine_is_maximizing=False, performance_test=True,
              update_hash=True, print_updates=True, score_only=False):
    clean_board = board
    board = copy.deepcopy(board)

    # Check if we are in an endgame
    if len(board.piece_map()) <= 7:
        try:
            tablebase_result = utils.evaluate_endgame(board)

            return {
                "eval": tablebase_result["eval"],
                "move": tablebase_result["move"],
                "depth": None,
                'alpha': None,
                'beta': None
            }

        except TablebaseLookupError:
            print("WARNING: Cannot connect to lichess.ovh for tablebase lookup. Ensure internet connection is stable.")

    # Check if we are in a book position
    opening_pgns = utils.load_openings()
    combined = '\t'.join(opening_pgns)
    board_pgn = utils.generate_pgn(board)

    if board_pgn in combined and allow_book:
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
            "depth": None,
            'alpha': None,
            'beta': None
        }

    best_move = None

    if print_updates:
        print("Searching...")

    try:
        # Iterative Deepening
        for depth in range(1, max_depth + 1):
            start_time = time.time()
            search = minimax(board, depth, float('-inf'), float('inf'), engine_is_maximizing,
                             hash=utils.ZobristHash(board))
            best_move = search["best_move"]

            if print_updates:
                if best_move:
                    print(f"\rDepth: {depth} | Move: {board.san(best_move)} | Score: {round(search['score'], 1)}", end='')
                else:
                    print(f"\rDepth: {depth}", end='')
            if score_only:
                print(f"\rDepth: {depth} | Score: {search['score']}", end='')

            # Abort when time limit is exceeded
            if time.time() - start_time >= constants["time_limit"] and best_move is not None:
                break

    except KeyboardInterrupt as e:
        raise e  # TODO: allow aborting

    if print_updates:
        print("\n")

    if update_hash:
        zobrist_hash.move(clean_board.parse_san(str(search["best_move"])), board)

    return {
        "move": str(search["best_move"]),
        "eval": search["score"],
        "depth": depth
    }
