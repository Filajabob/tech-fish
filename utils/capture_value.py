piece_values = {
    1: 1,
    2: 3,
    3: 3.5,
    4: 5,
    5: 9,
    6: float("inf")
}


def capture_value(board, move):
    if board.is_capture(move):
        victim = board.piece_at(move.to_square)
        attacker = board.piece_at(move.from_square)

        if not (victim and attacker):
            return 0

        return piece_values[victim.piece_type] - piece_values[attacker.piece_type]
    else:
        return 0
