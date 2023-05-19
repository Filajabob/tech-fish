# TechFish v1.0.0

Feast your eyes on the next horrible chess engine; TechFish!

This school assignment, using the minimax algorithm (plus optimizations) can (un)reliably search up to a depth of 4 in about 10 seconds.

If you think you are super cool, you can fiddle with the numbers in `assets/json/constants.json`.

## How to use

### Machine and Python Requirements

TechFish requires a minimum of Python 3.10 (as determined by [Vermin](https://github.com/netromdk/vermin)) on your machine. TechFish has been tested on Windows 10 only.

### Getting TechFish onto your computer

1. On the main GitHub project page, navigate to Releases > (Latest) > Assets> Source Code
2. Navigate to the downloaded ZIP / TAR.
3. Extract the folder.

### Python requirements

Because I'm such a cool guy, simply navigate to the directory in the command line, and run `pip install -r requirements.txt`

### And...

You're ready!

## Optimizations

This engine uses
- Alpha-Beta pruning
- Move Ordering (MVV-LVA, Transposition Table Ordering, Killer Moves)
- Transpositions (Zobrist hashing)
- Iterative Deepening
- Futility and Extended Futility Pruning
- Lazy SMP
- Quiescent Search
- Maybe more (I forgor)
