import chess
import utils

board = chess.Board()

player_is_white = input("Play as white? (Y/n) ") == "Y"

while True:
    san_move = input("Move: ")

    try:
        board.push_san(san_move)
        print(board)

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

