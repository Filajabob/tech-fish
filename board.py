import chess
import utils
from evaluate import evaluate_material, find_move

board = chess.Board()

while True:
    san_move = input("Move: ")

    try:
        board.push_san(san_move)
    except chess.IllegalMoveError:
        print("Illegal move!")
        continue

    print(board)
    print()

    # Evaluate future positions

    # Make the best move
    eval = find_move(board)
    board.push_san(eval["move"])

    print(board)
    print()
    print("Move:", utils.generate_san_move_list(board)[-1])
    print("Material Balance:", evaluate_material(board))
    print("Eval:", str(eval["eval"]))
    print()

    if board.outcome():
        outcome = board.outcome()
        if outcome.winner == True: winner = "White"
        if outcome.winner == False: winner = "Black"

        termination = str(outcome.termination).split('.')[1]

        print(f"{winner} won due to {termination}")
        break


