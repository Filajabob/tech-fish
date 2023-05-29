import chess
import utils

constants = utils.load_constants()


def evaluate_position(board):
    """Evaluates the current material of a singular position."""
    # If the game has ended, figure out who is winning
    if board.is_checkmate():
        return float('inf' if board.turn else '-inf')
    elif board.is_stalemate() or board.is_insufficient_material() or board.is_seventyfive_moves() or board.is_fivefold_repetition():
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

        return material_balance + piece_map_score
