import random
import math

class SudokuSolver:

    def __init__(self, grid):
        self.grid = grid
        self.flat_grid = [cell for row in self.grid for cell in row]
        self.size = len(grid)
        self.masks = [
            [True if self.grid[i][j] == 0 else False for j in range(self.size)]
            for i in range(self.size)
        ]

    def start_annealing(self, grid=None):
        self.grid = self.grid if grid is None else grid
        self.size = len(grid)
        self.box_size = int(math.sqrt(self.size))
        self.boxes_coors = []
        self.temperature = 1.0
        self.cooling_rate = 0.99
        self.max_swaps = 1000

        self.masks = [
            [True if self.grid[i][j] == 0 else False for j in range(self.size)]
            for i in range(self.size)
        ]

        self.fill_randomly()
        return self.simulated_annealing()

    def count_errors(self):
        errors = 0
        for i in range(self.size):
            row = [0] * (self.size + 1)
            col = [0] * (self.size + 1)

            for j in range(self.size):
                # Count errors in rows
                if row[self.grid[i][j]] == 1:
                    errors += 1
                row[self.grid[i][j]] += 1

                # Count errors in columns
                if col[self.grid[j][i]] == 1:
                    errors += 1
                col[self.grid[j][i]] += 1


        return errors

    def swap_cells(self, cell1, cell2):
        # Swap two cells in the grid
        self.grid[cell1[0]][cell1[1]], self.grid[cell2[0]][cell2[1]] = self.grid[cell2[0]][cell2[1]], self.grid[cell1[0]][cell1[1]]


    def fill_randomly(self):
        # Fill the grid randomly with values between 1 and size according to the masks
        for i in range(0, self.size, self.box_size):
            for j in range(0, self.size, self.box_size):
                
                box_coors = []
                numbers = list(range(1, self.size + 1))
                for k in range(i, i + self.box_size):
                    for l in range(j, j + self.box_size):
                        if not self.masks[k][l]:
                            numbers.remove(self.grid[k][l])

                
                for k in range(i, i + self.box_size):
                    for l in range(j, j + self.box_size):
                        if self.masks[k][l]:
                            self.grid[k][l] = random.choice(numbers)
                            numbers.remove(self.grid[k][l])

                            box_coors.append((k, l))
                            self.boxes_coors.append(box_coors)

                
    def print_grid(self):
        # Print the grid
        for row in self.grid:
            print(row)

    def simulated_annealing(self):
        current_errors = self.count_errors()
        
        best_errors = current_errors
        best_solution = self.grid.copy()

        for i in range(self.max_swaps):
            
            for box in self.boxes_coors:
                if len(box) == 1:
                    continue

                # Choose two random different cells in the box
                cell1 = random.choice(box)
                cell2 = random.choice(list(set(box) - set([cell1])))

                # Swap the cells and calculate the new errors
                self.swap_cells(cell1, cell2)
                new_errors = self.count_errors()
                

                # Calculate the acceptance probability
                if new_errors < current_errors:
                    acceptance_prob = 1.0
                else:
                    acceptance_prob = math.exp((current_errors - new_errors) / self.temperature)

                # Accept or reject the swap
                if random.random() < acceptance_prob:
                    current_errors = new_errors
                else:
                    self.swap_cells(cell1, cell2)

            # Update the temperature
            self.temperature *= self.cooling_rate

            # Check if we have found a better solution
            if current_errors < best_errors:
                best_errors = current_errors
                best_solution = self.grid.copy()

            if best_errors == 0:
                print(f'step {i}: solution found')
                break


        return best_solution, best_errors, self.masks


    def brute_force(self):

        def solve(sudoku_grid):
            """ 
            Solve a Sudoku puzzle.

            - Accepts `sudoku_grid`, a sequence of 81 integers from 0 to 9 representing the grid.
            Zeros indicate the cells to be filled.

            - Returns the first found solution as a sequence of 81 integers in the 1 to 9 interval
            (in the same order as input), or None if no solution exists.
            """
            
            try:
                empty_index = sudoku_grid.index(0)
            except ValueError:
                return sudoku_grid

            conflicting_values = [
                sudoku_grid[j] for j in range(81)
                if not ((empty_index - j) % 9 *                 # Same column
                        (empty_index // 9 ^ j // 9) *           # Same row
                        (empty_index // 27 ^ j // 27 |          # Same 3x3 block row-wise
                        (empty_index % 9 // 3 ^ j % 9 // 3)))  # Same 3x3 block column-wise
            ]            
            for value in range(1, 10):
                if value not in conflicting_values:
                    result = solve(sudoku_grid[:empty_index] + [value] + sudoku_grid[empty_index + 1:])
                    if result is not None:
                        return result

            # If no value can be placed in this cell without conflict, return None (backtrack)
            return None
    
        result = solve(self.flat_grid)
        grid = [[] for _ in range(9)]
        for i in range(81):
            grid[i // 9].append(result[i])

        return grid


def brute_solve(sudoku_grid):
    """ 
    Solve a Sudoku puzzle.

    - Accepts `sudoku_grid`, a sequence of 81 integers from 0 to 9 representing the grid.
    Zeros indicate the cells to be filled.

    - Returns the first found solution as a sequence of 81 integers in the 1 to 9 interval
    (in the same order as input), or None if no solution exists.
    """
    
    try:
        empty_index = sudoku_grid.index(0)
    except ValueError:
        return sudoku_grid

    conflicting_values = [
        sudoku_grid[j] for j in range(81)
        if not ((empty_index - j) % 9 *                 # Same column
                (empty_index // 9 ^ j // 9) *           # Same row
                (empty_index // 27 ^ j // 27 |          # Same 3x3 block row-wise
                (empty_index % 9 // 3 ^ j % 9 // 3)))  # Same 3x3 block column-wise
    ]            
    for value in range(1, 10):
        if value not in conflicting_values:
            result = brute_solve(sudoku_grid[:empty_index] + [value] + sudoku_grid[empty_index + 1:])
            if result is not None:
                return result

    # If no value can be placed in this cell without conflict, return None (backtrack)
    return None