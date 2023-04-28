import chess
import json


class TranspositionTable:
    def __init__(self):
        self.table = {}

    def get_raw_table(self):
        """
        Converts all chess.Moves to UCI format.
        :return: dict
        """

        raw_table = {}

        for key, values in self.table.items():
            if isinstance(values["best_move"], chess.Move):
                values["best_move"] = values["best_move"].uci()
            else:
                values["best_move"] = values["best_move"]

            raw_table[key] = values

        return raw_table

    def serialize(self, filepath):
        """
        Dump self.table into a JSON file
        :param filepath: Filepath to dump into
        """

        with open(filepath, 'w') as f:
            json.dump(self.get_raw_table(), f, indent=4)

    @staticmethod
    def load(filepath):
        self = TranspositionTable()

        with open(filepath, 'r') as f:
            self.table = json.load(f)

        return self

