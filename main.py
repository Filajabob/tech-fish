import time
import chess
import utils
from minimax import evaluate_position, find_move
from multiprocessing import Pool
import cProfile
import multiprocessing as mp

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

    profiler = cProfile.Profile()
    profiler.enable()

    eval = find_move(board, utils.load_constants()["max_depth"], utils.load_constants()["time_limit"], allow_book=allow_book,
                     engine_is_maximizing=maximizing)

    profiler.disable()
    profiler.dump_stats("profile.stats")

    time_spent = round(time.time() - start_time, 2)

    board.push_san(eval["move"])

    print_board(board, white)
    print()
    print("Move:", utils.generate_san_move_list(board)[-1])

    if isinstance(eval["eval"], float):
        print("Eval:", round(eval["eval"], 1))
    else:
        print("Eval:", str(eval["eval"]))

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
            if __name__ == '__main__':
                # Start pondering
                p = mp.Process(target=find_move, args=(board, 69, # depth is an arbitarily large number, for pondering
                                                   # purposes
                                                         utils.load_constants()["time_limit"]),
                                 kwargs={"allow_book": False, "engine_is_maximizing": white,
                                         "print_updates": False})
                p.start()
            san_move = input("Move: ")

            if __name__ == '__main__':
                p.terminate()
                p.join()

        except KeyboardInterrupt:
            print(utils.generate_pgn(board))
            print(board.fen())
            break

        try:
            board.push_san(san_move)

        except Exception as e:
            print(e)
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
                if __name__ == '__main__':
                    # Start pondering
                    p = mp.Process(target=find_move, args=(board, 69,
                                                       utils.load_constants()["time_limit"]),
                               kwargs={"allow_book": False, "engine_is_maximizing": white,
                                       "print_updates": False})
                    p.start()

                san_move = input("Move: ")

                if __name__ == '__main__':
                    p.terminate()
                    p.join()
            except KeyboardInterrupt:
                print(utils.generate_pgn(board))
                break

            try:
                board.push_san(san_move)
                break

            except Exception as e:
                print(e)
                continue

        print_board(board, white)
        print()
