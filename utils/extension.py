import chess
import utils


def extension(board, move, root, node_type):

    # CHECK EXTENSION

    if board.gives_check(move):
        return 1  # neutral extension

    # RECAPTURE EXTENSION

    if board.is_capture(move) and node_type == "exact":
        if utils.see_capture(move, board) >= 0:
            board.push(move)
            if utils.material_balance(board) == utils.material_balance(root):
                # Recapture extension
                board.pop()
                return 1
            else:
                board.pop()

    # PASSED PAWN EXTENSIONS

    if board.piece_at(move.from_square) == chess.PAWN:
        if board.turn == chess.WHITE and chess.square_rank(move.to_square) in (6, 7):
            # Pawn move by white, pawn is on 7th rank or promoted
            return 1
            pass
        elif board.turn == chess.BLACK and chess.square_rank(move.to_square) in (0, 1):
            # Pawn move by black, pawn is on 6th rank or promoted
            return 1
            pass

    return 0
