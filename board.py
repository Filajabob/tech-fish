import time
import chess
import utils
from minimax import evaluate_position, find_move
from multiprocessing import Pool

board = chess.Board(fen=utils.load_constants()["starting_fen"])
# TODO: FIX DISPLAY ISSUES: display_board = display.start()

white = input("Color (W/b) ") == "W"
inverse = input("Inverse board? (Y/n) ") == "Y"


def print_board(board, is_white):
    if is_white or (not is_white and inverse):
        # If white, or playing as black (but inverse is True)
        print(board)
    else:
        vertical_flipped = board.transform(chess.flip_vertical)
        print(vertical_flipped.transform(chess.flip_horizontal))


def find_and_make_move(board, maximizing=True, allow_book=True):
    start_time = time.time()
    eval = find_move(board, utils.load_constants()["max_depth"], utils.load_constants()["time_limit"], allow_book=allow_book,
                     engine_is_maximizing=maximizing)
    time_spent = round(time.time() - start_time, 2)

    board.push_san(eval["move"])

    print_board(board, white)
    print()
    print("Move:", utils.generate_san_move_list(board)[-1])

    if isinstance(eval["eval"], int):
        print("Eval:", round(eval["eval"], 2))
    else:
        print("Eval", str(eval["eval"]))

    print("Depth:", eval["depth"])
    print("Time Spent:", time_spent)
    print()


def end_game(board):
    outcome = board.outcome()
    if outcome.winner == True: winner = "White"
    if outcome.winner == False: winner = "Black"

    termination = str(outcome.termination).split('.')[1]

    print(f"{winner} won due to {termination}")
    print(utils.generate_pgn(board))
    print(board.fen())


while True:
    if white:
        try:
            san_move = input("Move: ")
        except KeyboardInterrupt:
            print(utils.generate_pgn(board))
            print(board.fen())
            break

        try:
            board.push_san(san_move)

        except chess.IllegalMoveError:
            print("Illegal move!")
            continue
        except chess.InvalidMoveError:
            print("Illegal move!")
            continue
        except chess.AmbiguousMoveError:
            print("Ambiguous move!")
            continue

        print_board(board, white)
        print()

        if board.outcome():
            end_game(board)
            break

        # Make the best move
        find_and_make_move(board, not white)

        if board.outcome():
            end_game(board)
            break
    else:
        # Make the best move
        find_and_make_move(board, not white)

        if board.outcome():
            end_game(board)
            break

        while True:
            try:
                san_move = input("Move: ")
            except KeyboardInterrupt:
                print(utils.generate_pgn(board))
                break

            try:
                board.push_san(san_move)
                break

            except chess.IllegalMoveError:
                print("Illegal move!")
                continue
            except chess.InvalidMoveError:
                print("Illegal move!")
                continue
            except chess.AmbiguousMoveError:
                print("Ambiguous move!")
                continue

        print_board(board, white)
        print()
