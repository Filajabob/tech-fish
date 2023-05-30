def extension(board, move):
    if board.gives_check(move):
        return 1  # neutral extension


    return 0
