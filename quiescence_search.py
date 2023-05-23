from evaluate_position import evaluate_position
import utils

constants = utils.load_constants()


def quiescence_search(board, alpha, beta, depth=constants["quiescent_depth"]):
    if depth == 0:
        return evaluate_position(board)

    stand_pat = evaluate_position(board)

    if stand_pat >= beta:
        return beta

    if alpha < stand_pat:
        alpha = stand_pat

    for capture in [move for move in board.legal_moves if board.is_capture(move) and utils.see_capture(move, board) > 0]:
        # Delta pruning
        BIG_DELTA = constants["piece_values"]["6"]

        if capture.promotion:
            BIG_DELTA += 7.75

        if stand_pat < alpha - BIG_DELTA:
            return alpha

        board.push(capture)
        score = -quiescence_search(board, -beta, -alpha, depth - 1)
        board.pop()

        if score >= beta:
            return beta

        if score > alpha:
            alpha = score

    return alpha

