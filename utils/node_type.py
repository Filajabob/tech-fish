def node_type(score, alpha, beta):
    if alpha < score < beta:
        return "exact"
    elif score <= alpha:
        return "upperbound"
    elif score >= beta:
        return "lowerbound"
