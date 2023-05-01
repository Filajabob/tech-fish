import chess
import json
import utils

constants = utils.load_constants()


class TranspositionTable:
    def __init__(self):
        self.table = {}

    def skim_table(self):
        """
        Deletes some entries to optimize RAM. This affects self.table AND returns the new skimmed table
        """

        entries = self.table.values()

        # Calculate total overflow, if any
        overflow = len(entries) - constants["max_transposition_entries"]

        if overflow <= 0:
            return

        sorted_entries = sorted(entries, key=lambda x: x["depth"], reverse=True)  # Sort based on depth
        del sorted_entries[-overflow:]

        self.table = sorted_entries

        return self.table


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

