import random

from textual.reactive import Reactive
from textual.views import GridView

from swept.cell import BOMB_CHAR, Cell, CellStatus
from swept.config import BOMB_PERCENT, N_COLS, N_ROWS
from swept.enums import GameStatus
from swept.exceptions import CantToggleFlag, CantUncover


class CellGrid(GridView):
    """
    Minesweeper-like game.
    """

    game_status = Reactive(GameStatus.IN_PROGRESS)

    def watch_game_status(self, game_status: GameStatus) -> None:
        """Control grid based on status."""
        if game_status == GameStatus.LOST:
            self.uncover_bombs()
        elif game_status == GameStatus.WON:
            for btn in self.cell_btns:
                if btn.status == CellStatus.FLAGGED:
                    btn.status = CellStatus.FLAGGED_WON

    def on_mount(self) -> None:
        """
        Event when widget is first mounted.
        """
        self.cell_btns = [
            Cell("", style=Cell.COVERED_CELL, name=f"{idx}")
            for idx in range(N_COLS * N_ROWS)
        ]
        self.reset_game()

        # set basic grid settings
        self.grid.set_gap(1, 1)
        self.grid.set_gutter(2)
        self.grid.set_align("center", "center")

        # create rows / columns / areas
        self.grid.add_column("col", max_size=6, repeat=N_COLS)
        self.grid.add_row("row", max_size=3, repeat=N_ROWS)

        self.grid.place(*self.cell_btns)

    def reset_game(self) -> None:
        """Reset game."""
        n_bombs = len(self.cell_btns) * BOMB_PERCENT // 100
        bombs = [True] * n_bombs + [False] * (len(self.cell_btns) - n_bombs)
        random.shuffle(bombs)

        for btn, bomb in zip(self.cell_btns, bombs):
            btn.value = BOMB_CHAR if bomb else ""

        for idx, btn in enumerate(self.cell_btns):
            if btn.value != BOMB_CHAR:
                btn.value = str(self.count_adjacent_bombs(idx))
            self.log(btn.value)
            btn.status = CellStatus.COVERED

    def uncover_cell(self, cell_idx: int) -> None:
        """Flip a cell."""
        cell = self.cell_btns[cell_idx]

        try:
            cell.uncover()
        except CantUncover:
            return

        # propagate 0 cell uncovering
        if cell.value == "0":
            for adj_idx in self._adjacent_idxs(cell_idx):
                self.uncover_cell(adj_idx)

    def uncover_bombs(self) -> None:
        """Uncover all bombs."""
        for btn in self.cell_btns:
            if btn.value == BOMB_CHAR and btn.status != CellStatus.EXPLODED:
                btn.status = CellStatus.UNCOVERED

    def uncover_adjacent(self, cell_idx: int) -> None:
        """Uncover adjacent cells if all bombs around a specific cell have been identified."""
        try:
            expected_bombs = int(self.cell_btns[cell_idx].label)
        except ValueError:
            return

        seen_bombs = sum(
            1
            for adj_idx in self._adjacent_idxs(cell_idx)
            if self.cell_btns[adj_idx].status == CellStatus.FLAGGED
        )

        if expected_bombs == seen_bombs:
            for adj_idx in self._adjacent_idxs(cell_idx):
                self.uncover_cell(adj_idx)

    def flag_cell(self, cell_idx: int) -> None:
        """Flag a cell where the player thinks is a bomb."""
        cell = self.cell_btns[cell_idx]

        try:
            cell.toggle_flag()
        except CantToggleFlag:
            return

    def win_condition(self) -> bool:
        """Compute if the game has been won."""
        return all(
            cell.status in [CellStatus.UNCOVERED, CellStatus.FLAGGED]
            for cell in self.cell_btns
        )

    def lose_condition(self) -> bool:
        """Compute if the game has been lost."""
        return any(cell.status == CellStatus.EXPLODED for cell in self.cell_btns)

    def _adjacent_idxs(self, idx: int) -> list[int]:
        """Compute all adjacent valid indices of a cell."""
        adjacents = []

        col = idx % N_COLS
        row = idx // N_COLS

        if col != 0 and row != 0:
            adjacents.append(idx - N_COLS - 1)
        if col != 0:
            adjacents.append(idx - 1)
        if col != 0 and row != N_ROWS - 1:
            adjacents.append(idx + N_COLS - 1)
        if row != 0:
            adjacents.append(idx - N_COLS)
        if row != N_ROWS - 1:
            adjacents.append(idx + N_COLS)
        if col != N_COLS - 1 and row != 0:
            adjacents.append(idx - N_COLS + 1)
        if col != N_COLS - 1:
            adjacents.append(idx + 1)
        if col != N_COLS - 1 and row != N_ROWS - 1:
            adjacents.append(idx + N_COLS + 1)

        return adjacents

    def count_adjacent_bombs(self, idx: int) -> int:
        """
        Compute the number of adjacent bombs to a cell.
        """
        return sum(
            1
            for adj_idx in self._adjacent_idxs(idx)
            if self.cell_btns[adj_idx].value == BOMB_CHAR
        )
