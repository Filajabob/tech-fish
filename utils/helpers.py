import utils
import copy

constants = utils.load_constants()


def start_helpers(abort_flag, board, depth, alpha, beta, is_maximizing, zobrist_hash):
    from minimax import minimax

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

    return helpers


def kill_helpers(abort_flag):
    abort_flag.set()
