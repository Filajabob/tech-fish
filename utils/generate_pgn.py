

def generate_pgn(board):
    moves = board.move_stack
    san_moves = [str(move) for move in moves]
    grouped_san_moves = list(zip(*[iter(san_moves)] * 2))

    pgn = ""
    i = 1

    for move in grouped_san_moves:
        pgn += f"{i}. {move[0]} {move[1]} "
