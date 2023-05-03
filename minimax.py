import random
import time
import re
import threading
import copy
import traceback

import chess
import psutil

import utils
from errors import *
from transposition_table import TranspositionTable
from evaluate_position import evaluate_position

constants = utils.load_constants()
transposition_table = TranspositionTable.load(constants["transpositions_filepath"])

zobrist_hash = utils.ZobristHash(chess.Board(constants["starting_fen"]))

abort_flag = threading.Event()


# TODO: Fix Zobrist hashing taking too long, or remove it


def minimax(board, depth, alpha, beta, is_maximizing, hash=zobrist_hash, thread=False, top=False):
    """
    A minimax evaluation function, which uses alpha-beta pruning, move ordering, and Zobrist hashing. Also uses Lazy SMP.
    :param stop:
    :param board:
    :param depth:
    :param alpha:
    :param beta:
    :param is_maximizing:
    :return:
    """

    initial_alpha = alpha
    initial_beta = beta

    hash_key = hash.current_hash

    # Check if there is an entry in the transposition table for this hash
    if transposition_table.entry_exists(hash_key):
        entry = transposition_table.get_entry(hash_key)
        if entry["depth"] >= depth:
            if entry["type"] == 'exact':
                return entry
            elif entry["type"] == 'lowerbound' and entry["score"] >= beta:
                return entry
            elif entry["type"] == 'upperbound' and entry["score"] <= alpha:
                return entry
            if alpha >= beta:
                return entry

    # If we reached the bottom of the tree, evaluate the position
    if depth == 0:
        score = evaluate_position(board)

        if score <= initial_alpha:
            type = "lowerbound"
        elif score >= initial_beta:
            type = "upperbound"
        else:
            type = None

        transposition_table.add_entry(hash_key, {
            "score": score,
            "best_move": None,
            "depth": depth,
            "type": type,
            'alpha': alpha,
            'beta': beta
        })

        return {
            "score": evaluate_position(board),
            "best_move": None,
            "depth": depth,
            'alpha': alpha,
            'beta': beta
        }

    if is_maximizing:
        # Find best move for the maximizing player (white)
        max_score = float('-inf')  # Currently, the best score that can be achieved
        best_move = None  # The best move

        if depth != 1 and not thread:
            abort_flag.clear()
            helpers = []

            # Start helper threads
            for i in range(constants["num_helper_threads"]):
                if i % 2 == 0:
                    increment = 1
                else:
                    increment = 0

                helper = utils.TracedThread(target=minimax, args=(copy.deepcopy(board), depth + increment, alpha, beta,
                                                                  is_maximizing, copy.deepcopy(zobrist_hash), True))
                helpers.append(helper)
                helper.start()

        for move in utils.order_moves(board, board.legal_moves, transposition_table, hash, depth):
            hash.move(move, board)  # Make sure the Zobrist Hash calculation happens before the move
            board.push(move)  # Try the move

            search = minimax(board, depth - 1, alpha, beta, False, thread=thread or not top)

            if search is None and not top:
                board.pop()
                zobrist_hash.pop(move, board)
                return
            elif search is None and top:
                board.pop()
                zobrist_hash.pop(move, board)
                continue

            score = search["score"]

            board.pop()
            zobrist_hash.pop(move, board)

            if score > max_score:
                max_score = score
                best_move = move

            alpha = max(alpha, max_score)

            if alpha >= beta:
                break

            if abort_flag.is_set() and not top:
                return

        if max_score <= initial_alpha:
            type = "lowerbound"
        elif max_score >= initial_beta:
            type = "upperbound"
        else:
            type = None

        transposition_table.add_entry(hash_key, {
            'score': max_score,
            'best_move': best_move,
            'depth': depth,
            "type": type,
            'alpha': alpha,
            'beta': beta
        })

        if depth != 1 and not thread:
            results = []

            abort_flag.set()

            results.append({
                'score': max_score,
                'best_move': best_move,
                'depth': depth,
                'alpha': alpha,
                'beta': beta
            })

            # Delete unfinished searches
            results = [result for result in results if result is not None]

            results = sorted(results, key=lambda x: x["depth"], reverse=True)  # Sort based on depth
            required_depth = results[0]["depth"]  # Get the highest depth

            results = [result for result in results if result["depth"] >= required_depth]  # Delete results which aren't deep enough

            results = sorted(results, key=lambda x: x["score"],
                             reverse=True)  # Sort based on greatest score (because we are maximizing)

            return results[0]

        return {
            'score': max_score,
            'best_move': best_move,
            'depth': depth,
            'alpha': alpha,
            'beta': beta
        }

    else:
        # Find best move for minimizing player (black)
        min_score = float('inf')
        best_move = None

        # Start helpers if depth is not 1 and helpers are allowed
        if depth != 1 and not thread:
            abort_flag.clear()
            helpers = []

            # Start helper threads
            for i in range(constants["num_helper_threads"]):
                if i % 2 == 0:
                    increment = 1
                else:
                    increment = 0

                helper = utils.TracedThread(target=minimax, args=(copy.deepcopy(board), depth + increment, alpha, beta,
                                                                  is_maximizing, copy.deepcopy(zobrist_hash), True))
                helpers.append(helper)
                helper.start()

        for move in utils.order_moves(board, board.legal_moves, transposition_table, hash, depth):
            hash.move(move, board)  # Make sure the Zobrist Hash calculation happens before the move
            board.push(move)

            search = minimax(board, depth - 1, alpha, beta, True, thread=thread or not top)

            if search is None and not top:
                board.pop()
                zobrist_hash.pop(move, board)
                return
            elif search is None and top:
                board.pop()
                zobrist_hash.pop(move, board)
                continue

            score = search["score"]

            board.pop()
            zobrist_hash.pop(move, board)  # Make sure the Zobrist Hash pop happens after the pop

            if score < min_score:
                min_score = score
                best_move = move

            beta = min(beta, min_score)

            if beta <= alpha:
                break

            if abort_flag.is_set() and not top:
                return

        if min_score <= initial_alpha:
            type = "lowerbound"
        elif min_score >= initial_beta:
            type = "upperbound"
        else:
            type = None

        transposition_table.add_entry(hash_key, {
            'score': min_score,
            'best_move': best_move,
            'depth': depth,
            "type": type,
            'alpha': alpha,
            'beta': beta
        })

        if depth != 1 and not thread:
            results = []

            abort_flag.set()

            results.append({
                'score': min_score,
                'best_move': best_move,
                'depth': depth,
                'alpha': alpha,
                'beta': beta
            })

            results = [result for result in results if result is not None]

            results = sorted(results, key=lambda x: x["depth"], reverse=True)  # Sort based on depth
            required_depth = results[0]["depth"]  # Get the highest depth

            results = [result for result in results if result["depth"] >= required_depth]  # Delete results which aren't deep enough

            results = sorted(results, key=lambda x: x["score"],
                             reverse=False)  # Sort based on lowest score (because we are minimizing)

            return results[0]

        return {
            'score': min_score,
            'best_move': best_move,
            'depth': depth,
            'alpha': alpha,
            'beta': beta
        }


def find_move(board, max_depth, time_limit, *, allow_book=True, engine_is_maximizing=False, performance_test=True, print_depth=True):
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
            "depth": None,
            'alpha': None,
            'beta': None
        }

    # Iterative Deepening
    for depth in range(1, max_depth + 1):
        if print_depth:
            print(f"\rDepth: {depth}", end='')

        alpha, beta = -float('inf'), float('inf')
        start_time = time.time()
        search = minimax(board, depth, alpha, beta, engine_is_maximizing, top=True)

        # Save the full search to the transposition table
        transposition_table.add_entry(zobrist_hash.current_hash, {
            'score': search["score"],
            'best_move': search["best_move"],
            'depth': depth,
            "type": "exact",
            'alpha': alpha,
            'beta': beta
        })

        # Abort when time limit is exceeded
        if time.time() - start_time >= constants["time_limit"]:
            break

    if print_depth:
        print("\n")

    zobrist_hash.move(board.parse_san(str(search["best_move"])), board)
    transposition_table.serialize(constants["transpositions_filepath"])

    return {
        "move": str(search["best_move"]),
        "eval": search["score"],
        "depth": depth
    }
