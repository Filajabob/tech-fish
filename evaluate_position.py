import chess
import utils

constants = utils.load_constants()


def evaluate_position(board):
    """Evaluates the current material of a singular position."""
    # If the game has ended, figure out who is winning
    outcome = board.outcome()
    if outcome:
        if outcome.result() in ["1-0", "0-1", "1/2-1/2"]:
            if outcome.result() == "1-0":
                return float("inf")
            elif outcome.result() == "0-1":
                return float("-inf")
            elif outcome.result() == "1/2-1/2":
                return 0

    else:
        # Evaluate material (positive is good for white, negative good for black)
        material_balance = utils.material_balance(board)

        piece_maps = constants["piece_maps"]
        piece_map_score = 0

        # Give a bonus for pieces aligning with the piece map
        for square in chess.SQUARES:
            if board.piece_at(square):
                piece = board.piece_at(square)
                if piece.color == chess.WHITE:
                    piece_map_score += piece_maps[str(piece.piece_type)][63 - square]
                else:
                    piece_map_score -= piece_maps[str(piece.piece_type)][square]

        # Penalize for repeating moves
        repeat_score = 0

        if len(board.move_stack) >= 3:
            if board.move_stack[-3] == board.move_stack[-1]:
                repeat_score += constants["repeat_score"]

        # # Incentivize pawn attacks
        # pawn_attack_score = 0
        #
        # # This means a pawn has taken something in the previous move, which is probably bad for us
        # prev_move = board.move_stack[-1]
        # if prev_move.drop == 1 and \
        #         chess.square_file(prev_move.from_square) != chess.square_file(
        #         prev_move.to_square):
        #     pawn_attack_score -= constants["pawn_attack_score"]

        return material_balance + piece_map_score
