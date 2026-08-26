"""Tests for the AC-3 + backtracking Sudoku CSP solver."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sudoku_solver import SudokuCSP, solve_sudoku, read_sudoku_from_file

PUZZLE = [
    [5, 3, 0, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    [0, 9, 8, 0, 0, 0, 0, 6, 0],
    [8, 0, 0, 0, 6, 0, 0, 0, 3],
    [4, 0, 0, 8, 0, 3, 0, 0, 1],
    [7, 0, 0, 0, 2, 0, 0, 0, 6],
    [0, 6, 0, 0, 0, 0, 2, 8, 0],
    [0, 0, 0, 4, 1, 9, 0, 0, 5],
    [0, 0, 0, 0, 8, 0, 0, 7, 9],
]

SOLUTION_FIRST_ROW = [5, 3, 4, 6, 7, 8, 9, 1, 2]


def test_solves_classic_puzzle():
    solved, solution = solve_sudoku([row[:] for row in PUZZLE])
    assert solved
    assert solution[0] == SOLUTION_FIRST_ROW


def test_solution_satisfies_all_constraints():
    solved, solution = solve_sudoku([row[:] for row in PUZZLE])
    assert solved

    for row in solution:
        assert sorted(row) == list(range(1, 10))

    for col in range(9):
        assert sorted(solution[r][col] for r in range(9)) == list(range(1, 10))

    for box_r in range(0, 9, 3):
        for box_c in range(0, 9, 3):
            box = [solution[r][c]
                   for r in range(box_r, box_r + 3)
                   for c in range(box_c, box_c + 3)]
            assert sorted(box) == list(range(1, 10))


def test_givens_are_preserved():
    solved, solution = solve_sudoku([row[:] for row in PUZZLE])
    assert solved
    for r in range(9):
        for c in range(9):
            if PUZZLE[r][c] != 0:
                assert solution[r][c] == PUZZLE[r][c]


def test_neighbours_are_twenty_per_cell():
    """Each cell shares a constraint with 20 others (8 row + 8 col + 4 box)."""
    csp = SudokuCSP([row[:] for row in PUZZLE])
    assert len(csp._get_neighbors(4, 4)) == 20


def test_initial_domains():
    csp = SudokuCSP([row[:] for row in PUZZLE])
    assert csp.domains[(0, 0)] == {5}          # a given
    assert csp.domains[(0, 2)] == set(range(1, 10))  # an empty cell


def test_reading_puzzle_from_file(tmp_path):
    f = tmp_path / "p.txt"
    f.write_text("\n".join("".join(str(v) for v in row) for row in PUZZLE))
    assert read_sudoku_from_file(str(f)) == PUZZLE


def test_malformed_file_rejected(tmp_path):
    f = tmp_path / "bad.txt"
    f.write_text("123\n456\n")
    with pytest.raises(ValueError, match="expected 9 rows"):
        read_sudoku_from_file(str(f))
