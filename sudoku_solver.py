from typing import List, Set, Tuple, Dict, Optional
from collections import deque
import copy


class SudokuCSP:
    """Sudoku puzzle as a CSP"""

    def __init__(self, puzzle: List[List[int]]):
        """Initialize the CSP with the puzzle"""
        self.size = 9
        self.box_size = 3
        self.puzzle = puzzle

        self.domains: Dict[Tuple[int, int], Set[int]] = {}
        self._initialize_domains()

        self.arcs = self._generate_binary_constraints()

        self.ac3_queue_lengths: List[int] = []
        self.nodes_explored = 0

    def _initialize_domains(self):
        """Initialize domains for each cell"""
        for i in range(self.size):
            for j in range(self.size):
                if self.puzzle[i][j] != 0:
                    self.domains[(i, j)] = {self.puzzle[i][j]}
                else:
                    self.domains[(i, j)] = set(range(1, 10))

    def _generate_binary_constraints(
        self,
    ) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """Generate all binary constraints (arcs) for the Sudoku puzzle"""
        arcs = []
        for i in range(self.size):
            for j in range(self.size):
                neighbors = self._get_neighbors(i, j)
                for neighbor in neighbors:
                    arcs.append(((i, j), neighbor))
        return arcs

    def _get_neighbors(self, row: int, col: int) -> Set[Tuple[int, int]]:
        """Get all neighbors of a cell (same row, column, or 3x3 box)"""
        neighbors = set()

        for j in range(self.size):
            if j != col:
                neighbors.add((row, j))

        for i in range(self.size):
            if i != row:
                neighbors.add((i, col))

        box_row = (row // self.box_size) * self.box_size
        box_col = (col // self.box_size) * self.box_size
        for i in range(box_row, box_row + self.box_size):
            for j in range(box_col, box_col + self.box_size):
                if (i, j) != (row, col):
                    neighbors.add((i, j))

        return neighbors

    def ac3(self) -> bool:
        """AC-3 algorithm implementation"""
        queue = deque(self.arcs)

        print(f"\n{'='*70}")
        print("AC-3 Algorithm Execution")
        print(f"{'='*70}")
        print(f"Initial queue size: {len(queue)} arcs")
        print(f"Total binary constraints: {len(self.arcs)} arcs")

        step = 0

        while queue:
            step += 1
            queue_length = len(queue)
            self.ac3_queue_lengths.append(queue_length)

            if step % 100 == 0 or queue_length < 50:
                print(f"Step {step}: Queue length = {queue_length}")

            (xi, xj) = queue.popleft()

            if self._revise(xi, xj):
                if len(self.domains[xi]) == 0:
                    print(f"\nAC-3 failed at step {step}")
                    print(f"Empty domain found for cell {xi}")
                    return False

                neighbors = self._get_neighbors(xi[0], xi[1])
                for xk in neighbors:
                    if xk != xj:
                        queue.append((xk, xi))

        print(f"\nAC-3 completed successfully")
        print(f"Total steps: {step}")
        print(
            f"Maximum queue length: {max(self.ac3_queue_lengths) if self.ac3_queue_lengths else 0}"
        )
        print(
            f"Average queue length: {sum(self.ac3_queue_lengths) / len(self.ac3_queue_lengths) if self.ac3_queue_lengths else 0:.2f}"
        )

        return True

    def _revise(self, xi: Tuple[int, int], xj: Tuple[int, int]) -> bool:
        """Revise domain of Xi given Xj"""
        revised = False
        if len(self.domains[xj]) == 1:
            value = list(self.domains[xj])[0]
            if value in self.domains[xi]:
                self.domains[xi].remove(value)
                revised = True
        return revised

    def is_solved(self) -> bool:
        """Check if puzzle is completely solved"""
        for i in range(self.size):
            for j in range(self.size):
                if len(self.domains[(i, j)]) != 1:
                    return False
        return True

    def is_valid_solution(self) -> bool:
        """Validate solution satisfies all constraints"""
        solution = self.get_solution()

        for i in range(self.size):
            row = [solution[i][j] for j in range(self.size)]
            if len(set(row)) != self.size or 0 in row:
                return False

        for j in range(self.size):
            col = [solution[i][j] for i in range(self.size)]
            if len(set(col)) != self.size or 0 in col:
                return False

        for box_row in range(0, self.size, self.box_size):
            for box_col in range(0, self.size, self.box_size):
                box = []
                for i in range(box_row, box_row + self.box_size):
                    for j in range(box_col, box_col + self.box_size):
                        box.append(solution[i][j])
                if len(set(box)) != self.size or 0 in box:
                    return False

        return True

    def get_solution(self) -> List[List[int]]:
        """Extract solution from domains"""
        solution = [[0] * self.size for _ in range(self.size)]
        for i in range(self.size):
            for j in range(self.size):
                if len(self.domains[(i, j)]) == 1:
                    solution[i][j] = list(self.domains[(i, j)])[0]
                else:
                    solution[i][j] = 0
        return solution

    def backtracking_search(self) -> bool:
        """Backtracking search with MRV heuristic"""
        print(f"\n{'='*70}")
        print("Backtracking Search with MRV Heuristic")
        print(f"{'='*70}")

        result = self._backtrack()

        print(f"\nBacktracking completed")
        print(f"Nodes explored: {self.nodes_explored}")

        return result

    def _backtrack(self) -> bool:
        """Recursive backtracking"""
        self.nodes_explored += 1

        if self.is_solved():
            if self.is_valid_solution():
                return True
            else:
                return False

        var = self._select_unassigned_variable()
        if var is None:
            return False

        values_to_try = list(self.domains[var])

        for value in sorted(values_to_try):
            saved_domains = copy.deepcopy(self.domains)
            self.domains[var] = {value}

            consistent = self._forward_checking(var, value)

            if consistent:
                result = self._backtrack()
                if result:
                    return True

            self.domains = saved_domains

        return False

    def _select_unassigned_variable(self) -> Optional[Tuple[int, int]]:
        """Select variable with MRV heuristic"""
        min_values = float("inf")
        selected_var = None

        for i in range(self.size):
            for j in range(self.size):
                domain_size = len(self.domains[(i, j)])
                if domain_size > 1 and domain_size < min_values:
                    min_values = domain_size
                    selected_var = (i, j)

        return selected_var

    def _forward_checking(self, var: Tuple[int, int], value: int) -> bool:
        """Forward checking - remove value from neighbor domains"""
        neighbors = self._get_neighbors(var[0], var[1])

        for neighbor in neighbors:
            if value in self.domains[neighbor]:
                self.domains[neighbor].remove(value)
                if len(self.domains[neighbor]) == 0:
                    return False

        return True

    def print_puzzle(self, puzzle: List[List[int]], title: str = "Sudoku Puzzle"):
        """Print formatted Sudoku puzzle"""
        print(f"\n{title}")
        print("+" + "-" * 25 + "+")

        for i in range(self.size):
            if i > 0 and i % 3 == 0:
                print("+" + "-" * 25 + "+")

            row_str = "| "
            for j in range(self.size):
                if j > 0 and j % 3 == 0:
                    row_str += "| "

                if puzzle[i][j] == 0:
                    row_str += ". "
                else:
                    row_str += f"{puzzle[i][j]} "

            row_str += "|"
            print(row_str)

        print("+" + "-" * 25 + "+")

    def print_domains_summary(self):
        """Print domain summary"""
        total_cells = self.size * self.size
        solved_cells = sum(1 for d in self.domains.values() if len(d) == 1)
        unsolved_cells = total_cells - solved_cells

        print(f"\n{'='*70}")
        print("Domain Summary")
        print(f"{'='*70}")
        print(f"Total cells: {total_cells}")
        print(f"Solved cells: {solved_cells}")
        print(f"Unsolved cells: {unsolved_cells}")

        if unsolved_cells > 0:
            print(f"\nUnsolved cells:")
            for i in range(self.size):
                for j in range(self.size):
                    if len(self.domains[(i, j)]) > 1:
                        print(
                            f"  Cell ({i},{j}): domain = {sorted(self.domains[(i, j)])}"
                        )


def read_sudoku_from_file(filename: str) -> List[List[int]]:
    """Read Sudoku puzzle from text file"""
    puzzle = []

    with open(filename, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            tokens = line.split()
            row = []
            for token in tokens:
                for char in token:
                    if char.isdigit():
                        row.append(int(char))
                    elif char in [".", "_"]:
                        row.append(0)

            if row:
                puzzle.append(row)

    if len(puzzle) != 9:
        raise ValueError(f"Invalid puzzle: expected 9 rows, got {len(puzzle)}")

    for i, row in enumerate(puzzle):
        if len(row) != 9:
            raise ValueError(
                f"Invalid puzzle: row {i} has {len(row)} cells, expected 9"
            )

    return puzzle


def solve_sudoku(puzzle: List[List[int]]) -> Tuple[bool, List[List[int]]]:
    """Solve Sudoku puzzle using CSP techniques"""
    csp = SudokuCSP(puzzle)

    csp.print_puzzle(puzzle, "Initial Puzzle")

    print(f"\n{'='*70}")
    print("CSP Representation - Binary Constraints")
    print(f"{'='*70}")
    print(f"Variables: {csp.size * csp.size} cells")
    print(f"Domain: {{1, 2, 3, 4, 5, 6, 7, 8, 9}} for empty cells")
    print(f"Binary Constraints: All-different constraint")
    print(f"  - Cells in same row must have different values")
    print(f"  - Cells in same column must have different values")
    print(f"  - Cells in same 3x3 box must have different values")
    print(f"Total arcs (binary constraints): {len(csp.arcs)}")

    ac3_success = csp.ac3()

    if not ac3_success:
        print("\nAC-3 detected inconsistency - no solution exists")
        return False, puzzle

    if csp.is_solved():
        solution = csp.get_solution()
        csp.print_puzzle(solution, "Solution (found by AC-3 alone)")
        print("\nPuzzle solved by AC-3 algorithm alone")
        return True, solution

    csp.print_domains_summary()

    print("\nPuzzle not completely solved by AC-3 alone")
    print("Applying backtracking search with MRV heuristic...")

    bt_success = csp.backtracking_search()

    if bt_success:
        solution = csp.get_solution()
        csp.print_puzzle(solution, "Solution (found by AC-3 + Backtracking)")
        print("\nPuzzle solved successfully")
        return True, solution
    else:
        print("\nNo solution found")
        return False, puzzle


def main():
    """Main function"""
    import sys

    if len(sys.argv) > 1:
        filename = sys.argv[1]
        print(f"Reading puzzle from: {filename}")
        puzzle = read_sudoku_from_file(filename)
    else:
        print("No input file provided. Using example puzzle.")
        puzzle = [
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

    success, solution = solve_sudoku(puzzle)

    if success:
        print(f"\n{'='*70}")
        print("SUCCESS - Puzzle solved")
        print(f"{'='*70}")
    else:
        print(f"\n{'='*70}")
        print("FAILED - Could not solve puzzle")
        print(f"{'='*70}")


if __name__ == "__main__":
    main()
