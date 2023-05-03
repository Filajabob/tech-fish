import hashlib
import chess
import json
import threading
import utils
import copy

constants = utils.load_constants()


class TranspositionTable:
    def __init__(self):
        """
        A transposition table which uses Zobrist hashing. Compatible with Lazy SMP.
        """
        self.table = {}
        self.TABLESIZE = 2 ** 20

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

    def serialize(self, filepath, *, skim=True):
        """
        Dump self.table into a JSON file
        :param skim: Whether to skim the table.
        :param filepath: Filepath to dump into
        """

        if skim:
            self.skim_table()

        with open(filepath, 'w') as f:
            json.dump(self.get_raw_table(), f, indent=4)

    def dict_to_int(self, d):
        # Use the hash of the string representation of the dictionary as the integer value
        hash_val = hashlib.sha256(str(d).encode('utf-8')).hexdigest()
        # Convert the hash value to an integer using base 16 (hexadecimal)
        int_val = int(hash_val, 16)
        return int_val

    def add_entry(self, hash, entry: dict):
        index = hash % self.TABLESIZE  # Generate an index
        key = hash ^ self.dict_to_int(entry)  # Use Lock-less XOR to generate a key
        entry["key"] = key  # Set the key

        self.table[index] = entry

    def get_entry(self, hash):
        index = hash % self.TABLESIZE

        if not self.entry_exists(hash):
            raise KeyError(hash)

        entry = copy.copy(self.table[index])
        del entry["key"]

        return entry

    def entry_exists(self, hash):
        index = hash % self.TABLESIZE

        # Index doesn't exist
        if index not in self.table:
            return False

        entry = copy.copy(self.table[index])
        del entry["key"]

        if not (self.table[index]["key"] ^ self.dict_to_int(entry) == hash):
            # Key doesn't match original hash
            return False
        else:
            # Index exists, keys match
            return True

    @staticmethod
    def load(filepath):
        self = TranspositionTable()

        with open(filepath, 'r') as f:
            self.table = json.load(f)

        return self
