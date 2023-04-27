def order_moves(board, moves):
    """
    Orders the given list of moves according to a simple heuristic:
    captures first, then promotions, then checks, then other moves.
    """
    captures = []
    promotions = []
    checks = []
    other_moves = []

    for move in moves:
        if board.is_capture(move):
            captures.append(move)
        elif move.promotion:
            promotions.append(move)
        elif board.gives_check(move):
            checks.append(move)
        else:
            other_moves.append(move)

    return captures + promotions + checks + other_moves
