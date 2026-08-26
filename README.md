# Sudoku CSP Solver

Solves Sudoku by treating it as a **constraint satisfaction problem** rather than searching brute force: AC-3 arc consistency prunes the search space first, and backtracking with the MRV heuristic and forward checking handles whatever constraint propagation alone can't finish.

Easy puzzles are often solved by **AC-3 alone, with zero search**.

## How it works

A Sudoku grid is modelled as 81 variables (one per cell), each with domain `{1..9}`, connected by 1,944 binary "all-different" constraints — every cell shares a constraint with the 20 others in its row, column, and 3×3 box.

| Stage | Technique | What it does |
|---|---|---|
| 1 | **AC-3 arc consistency** | Repeatedly removes values that can't participate in any valid assignment. Detects unsolvable puzzles early by finding an empty domain. |
| 2 | **Backtracking search** | Only runs if AC-3 leaves cells undecided. |
| 3 | **MRV heuristic** | Selects the most-constrained cell next (fewest remaining values), which fails fast and prunes hard. |
| 4 | **Forward checking** | After each assignment, removes that value from neighbours and abandons the branch the moment any domain empties. |

The solver reports its own work — AC-3 queue length over time, cells resolved by propagation vs. search, and nodes explored — so you can see where the effort actually went on a given puzzle.

## Running it

```bash
pip install -r requirements.txt 2>/dev/null; python sudoku_solver.py puzzles/hard.txt
```

With no argument it solves a built-in example. Puzzle files are 9 rows of 9 digits, using `0`, `.`, or `_` for blanks:

```
530070000
600195000
098000060
```

Included puzzles: `very_easy`, `easy`, `medium`, `hard`, `expert`.

## Tests

```bash
python -m pytest tests/ -q
```

7 tests covering constraint generation, domain initialisation, the full solve path, given-preservation, and malformed-input handling. The solution test independently re-verifies all 27 row/column/box constraints rather than trusting the solver's own validator.

## Built with

Python 3, standard library only — no solver libraries. The CSP machinery is implemented from scratch.
