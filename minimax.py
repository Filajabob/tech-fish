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
from quiescence_search import quiescence_search

constants = utils.load_constants()
# transposition_table = TranspositionTable.load(constants["transpositions_filepath"])
transposition_table = TranspositionTable()

zobrist_hash = utils.ZobristHash(chess.Board(constants["starting_fen"]))

abort_flag = threading.Event()

killer_moves = {
    chess.WHITE: [[]] * 30,
    chess.BLACK: [[]] * 30
}


# TODO: Fix Zobrist hashing taking too long, or remove it


def minimax(board, depth, alpha, beta, is_maximizing, hash=zobrist_hash, thread=False, main_search=False,
            first_move=None, allow_null=True, allow_threads=True):
    """
    A minimax evaluation function, which uses alpha-beta pruning, move ordering, and Zobrist hashing. Also uses Lazy SMP.
    :param first_move: The current best move from the previous iterative deepening search, will be evaluated first
    :param main_search: If this is part of the main search
    :param thread: If the function is being called from a thread
    :param hash:
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

    # If we reached the bottom of the tree, or if position is quiet, start quiescent search
    if depth == 0 or utils.is_quiescent(board):
        score = quiescence_search(board, alpha, beta)

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

    # Null move pruning

    if allow_null and not board.is_check() and depth - 1 - constants["R"] > 0:
        null_move = chess.Move.null()

        hash.move(null_move, board)
        board.push(null_move)

        search = minimax(board, depth - 1 - constants["R"], -beta, -beta + 1, not is_maximizing, hash,
                         allow_null=False, allow_threads=False)
        score = -search["score"]

        board.pop()
        hash.pop(null_move, board)

        if score >= beta:
            return search

    # Futility Pruning

    if depth == 1 and not board.is_check() and alpha != float("inf") and beta != float("-inf"):
        if not evaluate_position(board) + constants["piece_values"]["4"] > alpha:
            # evaluate captures and checks
            moves = [move for move in board.legal_moves if board.is_capture(move) or board.gives_check(move)]
        else:
            moves = board.legal_moves
    else:
        moves = board.legal_moves

    ordered_moves = utils.order_moves(board, moves, transposition_table, hash, depth,
                                      killer_moves=killer_moves, best_move=first_move)

    if is_maximizing:
        # Find best move for the maximizing player (white)
        max_score = float('-inf')  # Currently, the best score that can be achieved
        best_move = None  # The best move

        if not thread and allow_threads:
            # We are in the main thread, start helpers
            utils.start_helpers(abort_flag, board, depth, alpha, beta, is_maximizing, hash)

        for i, move in enumerate(ordered_moves):
            search_depth = depth - 1
            if i > constants["lmr_sampling"] - 1:
                search_depth -= constants["reduction"]
                search_depth = max(search_depth, 0)

            hash.move(move, board)  # Make sure the Zobrist Hash calculation happens before the move
            board.push(move)  # Try the move

            search = minimax(board, search_depth, alpha, beta, not is_maximizing, hash, thread or not main_search,
                             main_search=main_search)

            board.pop()
            hash.pop(move, board)

            if search is None and not main_search:
                return
            elif search is None and main_search:
                continue

            score = search["score"]

            if score > max_score:
                max_score = score
                best_move = move

            alpha = max(alpha, max_score)

            if score > alpha:
                killer_moves[board.turn][depth].append(move)

            if alpha >= beta:
                break

            if abort_flag.is_set() and not main_search:
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

        utils.kill_helpers(abort_flag)

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
        if not thread and allow_threads:
            utils.start_helpers(abort_flag, board, depth, alpha, beta, is_maximizing, hash)

        for i, move in enumerate(ordered_moves):
            search_depth = depth - 1
            if i > constants["lmr_sampling"] - 1:
                search_depth -= constants["reduction"]
                search_depth = max(search_depth, 0)

            hash.move(move, board)  # Make sure the Zobrist Hash calculation happens before the move
            board.push(move)

            search = minimax(board, search_depth, alpha, beta, not is_maximizing, thread=thread or not main_search,
                             main_search=main_search)

            board.pop()
            hash.pop(move, board)

            if search is None and not main_search:
                return
            elif search is None and main_search:
                continue

            score = search["score"]

            if score < min_score:
                min_score = score
                best_move = move

            beta = min(beta, min_score)

            if score < beta:
                killer_moves[board.turn][depth].append(move)

            if beta <= alpha:
                break

            if abort_flag.is_set() and not main_search:
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

        utils.kill_helpers(abort_flag)

        return {
            'score': min_score,
            'best_move': best_move,
            'depth': depth,
            'alpha': alpha,
            'beta': beta
        }


def find_move(board, max_depth, time_limit, *, allow_book=True, engine_is_maximizing=False, performance_test=True,
              update_hash=True, print_updates=True):
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

    best_move = None

    print("Searching...")

    starting_board = copy.copy(board)

    try:
        # Iterative Deepening
        for depth in range(1, max_depth + 1):
            if print_updates:
                if best_move:
                    print(f"\rDepth: {depth} | Move: {board.san(best_move)}", end='')
                else:
                    print(f"\rDepth: {depth}", end='')

            alpha, beta = -float('inf'), float('inf')
            start_time = time.time()
            search = minimax(board, depth, alpha, beta, engine_is_maximizing, main_search=True, first_move=best_move)
            best_move = search["best_move"]

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
            if time.time() - start_time >= constants["time_limit"] and best_move is not None:
                break

    except KeyboardInterrupt as e:
        raise e  # TODO: allow aborting

    if print_updates:
        print("\n")

    if update_hash:
        zobrist_hash.move(clean_board.parse_san(str(search["best_move"])), board)
    # transposition_table.serialize(constants["transpositions_filepath"])

    return {
        "move": str(search["best_move"]),
        "eval": search["score"],
        "depth": depth
    }
