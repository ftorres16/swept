import enum
import random

from textual.app import App
from textual.reactive import Reactive
from textual.views import GridView

from swept.cell import BOMB_CHAR, Cell, CellStatus, LeftClick, MiddleClick, RightClick
from swept.exceptions import CantToggleFlag, CantUncover


N_COLS = 10
N_ROWS = 10
BOMB_PERCENT = 20


class GameStatus(enum.Enum):
    IN_PROGRESS = enum.auto()
    WON = enum.auto()
    LOST = enum.auto()


def adjacent_idxs(idx: int) -> list[int]:
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


def count_bombs(cells: list[str], idx: int) -> str:
    """
    Compute the number of adjacent bombs to a cell.
    """
    if cells[idx] == BOMB_CHAR:
        return BOMB_CHAR

    bombs = sum(1 for adj_idx in adjacent_idxs(idx) if cells[adj_idx] == BOMB_CHAR)

    return str(bombs)


class Swept(GridView):
    """
    Minesweeper-like game.
    """

    game_status = Reactive(GameStatus.IN_PROGRESS)

    def watch_game_status(self, game_status: GameStatus) -> None:
        """Control game based on status."""
        if game_status == GameStatus.LOST:
            self.uncover_bombs()
            self.log("Game over!")
        elif game_status == GameStatus.WON:
            self.log("Game won!")
            for btn in self.cell_btns:
                if btn.status == CellStatus.FLAGGED:
                    btn.status = CellStatus.FLAGGED_WON
                    # btn.button_style = btn.WON_CELL
                    # btn.label = btn.label + " "

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
        cells_txt = [BOMB_CHAR] * (N_COLS * N_ROWS * BOMB_PERCENT // 100) + [""] * (
            N_COLS * N_ROWS - N_COLS * N_ROWS * BOMB_PERCENT // 100
        )
        random.shuffle(cells_txt)
        for idx, _ in enumerate(cells_txt):
            cells_txt[idx] = count_bombs(cells_txt, idx)

        for cell, txt in zip(self.cell_btns, cells_txt):
            cell.value = txt
            cell.status = CellStatus.COVERED

        self.game_status = GameStatus.IN_PROGRESS

    def handle_left_click(self, message: LeftClick) -> None:
        """Left click on a cell in the grid."""
        if self.game_status != GameStatus.IN_PROGRESS:
            return
        self.uncover_cell(int(message.sender.name))

    def handle_middle_click(self, message: MiddleClick) -> None:
        """Middle click on a cell in the grid."""
        if self.game_status != GameStatus.IN_PROGRESS:
            return
        self.uncover_adjacent(int(message.sender.name))

    def handle_right_click(self, message: RightClick) -> None:
        """Right click on a cell in the grid."""
        if self.game_status != GameStatus.IN_PROGRESS:
            return
        self.flag_cell(int(message.sender.name))

    def uncover_cell(self, cell_idx: int) -> None:
        """Flip a cell."""
        cell = self.cell_btns[cell_idx]

        try:
            cell.uncover()
        except CantUncover:
            return

        if cell.status == CellStatus.EXPLODED:
            self.game_status = GameStatus.LOST

        if self.win_condition():
            self.game_status = GameStatus.WON

        # propagate 0 cell uncovering
        if cell.value == "0":
            for adj_idx in adjacent_idxs(cell_idx):
                self.uncover_cell(adj_idx)

    def uncover_bombs(self) -> None:
        """Uncover all bombs."""
        for btn in self.cell_btns:
            if btn.value == BOMB_CHAR and btn.status != CellStatus.EXPLODED:
                btn.status = CellStatus.UNCOVERED

    def uncover_adjacent(self, cell_idx: int) -> None:
        """Uncover adjacent cells if all bombs have been identified."""
        try:
            expected_bombs = int(self.cell_btns[cell_idx].label)
        except ValueError:
            return

        seen_bombs = sum(
            1
            for adj_idx in adjacent_idxs(cell_idx)
            if self.cell_btns[adj_idx].status == CellStatus.FLAGGED
        )

        if expected_bombs == seen_bombs:
            for adj_idx in adjacent_idxs(cell_idx):
                self.uncover_cell(adj_idx)

    def flag_cell(self, cell_idx: int) -> None:
        """Flag a cell where the player thinks is a bomb."""
        cell = self.cell_btns[cell_idx]

        try:
            cell.toggle_flag()
        except CantToggleFlag:
            return

        if self.win_condition():
            self.game_status = GameStatus.WON

    def win_condition(self) -> bool:
        """Compute if the game has been won."""
        return all(
            cell.status in [CellStatus.UNCOVERED, CellStatus.FLAGGED]
            for cell in self.cell_btns
        )


class SweptApp(App):
    """The game application."""

    async def on_load(self, event):
        await self.bind("q", "quit")
        await self.bind("r", "reset")

    async def on_mount(self) -> None:
        self.cell_grid = Swept()

        await self.view.dock(self.cell_grid)

    async def action_reset(self) -> None:
        self.cell_grid.reset_game()


if __name__ == "__main__":
    SweptApp.run(log="textual.log")
