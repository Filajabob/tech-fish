# TechFish v1.1.1

Feast your eyes on the next horrible chess engine; TechFish!

This school assignment, using the minimax algorithm (plus optimizations) can (un)reliably search up to a depth of 4 in about 10 seconds.

If you think you are super cool, you can fiddle with the numbers in `assets/json/constants.json`.

## How to use

### Option 1: Using frozen code (using TechFish.exe) 

**This is the preferred method for using Tech Fish. Python is not required on your computer.**

#### Getting TechFish source code onto your computer

1. On the main GitHub project page, navigate to Releases > (Latest) > Assets > Source Code
2. Navigate to the downloaded ZIP / TAR.
3. Extract the folder.

#### Downloading and preparing frozen file (TechFish.exe)

1. On the main GitHub project page, navigate to Releases > (Latest) > Assets > TechFish.exe
2. Navigate to the EXE.
3. Move the EXE into the previously downloaded folder
4. (Optional) Create a shortcut to the file.


### Option 2: Running main.py with Python

#### Machine and Python Requirements

If you are not using EXE (ie. you are directly running main.py), TechFish requires a minimum of Python 3.10 
(as determined by [Vermin](https://github.com/netromdk/vermin)) on your machine. 

TechFish has been **tested on Windows 10 only**. It theoretically should work on other versions of Windows.

#### Getting TechFish onto your computer

1. On the main GitHub project page, navigate to Releases > (Latest) > Assets > Source Code
2. Navigate to the downloaded ZIP / TAR.
3. Extract the folder.

#### Packages

Because I'm such a cool guy, simply navigate to the directory in the command line, and run `pip install -r requirements.txt`

If you're curious, you can see all necessary packages and their roles in `requirements.txt`.

`psutil` is for performance tests / debugging, so if you won't use it, you can choose not to install it.

#### Running the engine

You're ready! Run `main.py` and follow the given instructions in the console.



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

## Example Games

### Spencer (W) vs. TechFish (B)
![board (5)](https://github.com/Filajabob/tech-fish/assets/98435043/4fe40c4a-eec8-4eb8-aad4-2a64244f7fb8)

