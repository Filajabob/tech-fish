import chess
import utils
from evaluate import evaluate_material, find_move

board = chess.Board()

while True:
    san_move = input("Move: ")

    try:
        board.push_san(san_move)
        print(board)
        print()

        # Evaluate future positions

        # Make the best move
        generated_move = find_move(board)
        board.push_san(generated_move)

        print(board)
        print("Move:", generated_move)
        print("Material Balance:", evaluate_material(board))
        print()

        if board.outcome():
            outcome = board.outcome()
            if outcome.winner == True: winner = "White"
            if outcome.winner == False: winner = "Black"

            termination = str(outcome.termination).split('.')[1]

            print(f"{winner} won due to {termination}")
            break
    except chess.IllegalMoveError:
        print("Illegal move!")
        continue

