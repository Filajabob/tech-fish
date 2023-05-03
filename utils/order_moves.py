def order_moves(board, moves, transposition_table, hash, depth, iid=False):
    """
    Orders the given list of moves according to a simple heuristic:
    captures first, then promotions, then checks, then other moves.

    Also uses the PV heuristic.
    """

    starters = []

    if transposition_table.entry_exists(hash.current_hash):
        entry = transposition_table.get_entry(hash.current_hash)
        if entry["type"] == "exact":
            # PV heuristic
            starters = [entry["best_move"]]

    if not starters and depth - 2 > 0 and iid:
        # No PV move could be found, use IID
        from minimax import minimax

        starters = [minimax(board, round(depth - 2), float("-inf"), float("inf"), board.turn)["best_move"]]

    starters = [starter for starter in starters if starter is not None]

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
        elif move in starters:
            continue  # delete the moves already added to the front
        else:
            other_moves.append(move)

    return starters + captures + promotions + checks + other_moves
