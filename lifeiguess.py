import random
from typing import List, Tuple, Optional

class Cell:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.is_alive = False

    def __repr__(self) -> str:
        return f"Cell({self.x}, {self.y}, is_alive={self.is_alive})"

    def set_alive(self, alive: bool = True) -> None:
        self.is_alive = alive

    def neighbors(self, grid_size: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Return valid neighbors for the cell within the grid boundaries."""
        x_max, y_max = grid_size
        potential_neighbors = [
            (self.x + dx, self.y + dy)
            for dx in (-1, 0, 1)
            for dy in (-1, 0, 1)
            if not (dx == 0 and dy == 0)
        ]
        return [
            (nx, ny)
            for nx, ny in potential_neighbors
            if 0 <= nx < x_max and 0 <= ny < y_max
        ]


class GameOfLife:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.grid = [[Cell(x, y) for y in range(height)] for x in range(width)]

    def __repr__(self) -> str:
        return f"GameOfLife({self.width}x{self.height})"

    def randomize(self, alive_probability: float = 0.2) -> None:
        """Randomly set cells to alive based on a given probability."""
        for row in self.grid:
            for cell in row:
                cell.set_alive(random.random() < alive_probability)

    def count_alive_neighbors(self, cell: Cell) -> int:
        """Count the number of alive neighbors around a given cell."""
        alive_count = 0
        for nx, ny in cell.neighbors((self.width, self.height)):
            if self.grid[nx][ny].is_alive:
                alive_count += 1
        return alive_count

    def next_generation(self) -> None:
        """Transition to the next generation of the grid."""
        updates = []
        for row in self.grid:
            for cell in row:
                alive_neighbors = self.count_alive_neighbors(cell)
                if cell.is_alive and alive_neighbors not in (2, 3):
                    updates.append((cell, False))  # Die from under/overpopulation
                elif not cell.is_alive and alive_neighbors == 3:
                    updates.append((cell, True))  # Revive by reproduction

        # Apply updates after calculations
        for cell, alive in updates:
            cell.set_alive(alive)

    def display(self) -> None:
        """Print the grid to the console."""
        for row in self.grid:
            print("".join("█" if cell.is_alive else " " for cell in row))
        print()


# Example usage
if __name__ == "__main__":
    game = GameOfLife(width=20, height=10)
    game.randomize(alive_probability=0.3)
    game.display()

    for _ in range(10):  # Simulate 10 generations
        game.next_generation()
        game.display()
