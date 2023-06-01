import utils


def extension(board, move, root, node_type):
    if board.gives_check(move):
        # Check extension
        return 1  # neutral extension

    if board.is_capture(move):
        board.push(move)
        if utils.material_balance(board) == utils.material_balance(root):
            # Recapture extension
            board.pop()
            return 1
        else:
            board.pop()

    return 0
