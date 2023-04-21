import time
import chess
import utils
from evaluate import evaluate_position, find_move
from multiprocessing import Pool

board = chess.Board(fen=utils.load_constants()["starting_fen"])
# TODO: FIX DISPLAY ISSUES: display_board = display.start()

print(board)
print()

while True:
    san_move = input("Move: ")

    try:
        board.push_san(san_move)

    except chess.IllegalMoveError:
        print("Illegal move!")
        continue
    except chess.InvalidMoveError:
        print("Illegal move!")
        continue

    print(board)
    print()

    # Evaluate future positions

    # Make the best move
    start_time = time.time()
    eval = find_move(board, utils.load_constants()["max_depth"], utils.load_constants()["time_limit"])
    time_spent = round(time.time() - start_time, 2)

    board.push_san(eval["move"])

    print(board)
    print()
    print("Move:", utils.generate_san_move_list(board)[-1])
    print("Eval:", str(eval["eval"]))
    print("Depth:", eval["depth"])
    print("Time Spent:", time_spent)
    print()

    if board.outcome():
        outcome = board.outcome()
        if outcome.winner == True: winner = "White"
        if outcome.winner == False: winner = "Black"

        termination = str(outcome.termination).split('.')[1]

        print(f"{winner} won due to {termination}")
        break
