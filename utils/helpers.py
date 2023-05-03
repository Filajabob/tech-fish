import utils

constants = utils.load_constants()


def start_helpers(abort_flag, board, depth, alpha, beta, is_maximizing, zobrist_hash):
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


def kill_helpers(abort_flag, helpers):
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

    results = [result for result in results if
               result["depth"] >= required_depth]  # Delete results which aren't deep enough

    results = sorted(results, key=lambda x: x["score"],
                     reverse=True)  # Sort based on greatest score (because we are maximizing)

    return results[0]