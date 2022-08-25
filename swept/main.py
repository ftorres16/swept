import random

from textual.app import App
from textual.views import GridView

from swept.cell import Cell, LeftClick, MiddleClick, RightClick


N_COLS = 10
N_ROWS = 10
BOMB_PERCENT = 20

BOMB_CHAR = ":bomb:"
FLAG_CHAR = ":triangular_flag:"


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


def count_bombs(cell: list[str], idx: int) -> str:
    """
    Compute the number of adjacent bombs to a cell.
    """
    if cell[idx] == BOMB_CHAR:
        return BOMB_CHAR

    bombs = sum(1 for adj_idx in adjacent_idxs(idx) if cell[adj_idx] == BOMB_CHAR)

    return str(bombs)


class Swept(GridView):
    """
    Minesweeper-like game.
    """

    CLEAR_CELL = "rgb(112,128,144) on rgb(112,128,144)"
    PRESSED_CELL = "white on rgb(16,16,16)"
    BOMB_CELL = "white on red"

    game_over = False

    def on_mount(self) -> None:
        """
        Event when widget is first mounted.
        """
        self.cells_txt = [":bomb:"] * (N_COLS * N_ROWS * BOMB_PERCENT // 100) + [
            "N"
        ] * (N_COLS * N_ROWS - N_COLS * N_ROWS * BOMB_PERCENT // 100)
        random.shuffle(self.cells_txt)
        for idx, _ in enumerate(self.cells_txt):
            self.cells_txt[idx] = count_bombs(self.cells_txt, idx)

        self.cell_btns = [
            Cell("", style=self.CLEAR_CELL, name=f"{idx}")
            for idx, _ in enumerate(self.cells_txt)
        ]

        # set basic grid settings
        self.grid.set_gap(1, 1)
        self.grid.set_gutter(2)
        self.grid.set_align("center", "center")

        # create rows / columns / areas
        self.grid.add_column("col", max_size=6, repeat=N_COLS)
        self.grid.add_row("row", max_size=3, repeat=N_ROWS)

        self.grid.place(*self.cell_btns)

    def handle_left_click(self, message: LeftClick) -> None:
        """Left click on a cell in the grid."""
        if self.game_over:
            return
        self.uncover_cell(int(message.sender.name))

    def handle_middle_click(self, message: MiddleClick) -> None:
        """Middle click on a cell in the grid."""
        if self.game_over:
            return

        self.uncover_adjacent(int(message.sender.name))

    def handle_right_click(self, message: RightClick) -> None:
        """Right click on a cell in the grid."""
        if self.game_over:
            return
        self.flag_cell(int(message.sender.name))

    def uncover_cell(self, cell_idx: int) -> None:
        """Flip a cell."""
        cell_txt = self.cells_txt[cell_idx]

        if (
            self.cell_btns[cell_idx].button_style == self.PRESSED_CELL
            or self.cell_btns[cell_idx].label == FLAG_CHAR
        ):
            # don't do anything to cells already turned or flagged
            return

        if cell_txt == BOMB_CHAR:
            self.game_over = True
            self.cell_btns[cell_idx].button_style = self.BOMB_CELL
            self.uncover_bombs()
        else:
            self.cell_btns[cell_idx].button_style = self.PRESSED_CELL

        if cell_txt == "0":
            cell_txt = " "

            # propagate 0 cells
            for adj_idx in adjacent_idxs(cell_idx):
                self.uncover_cell(adj_idx)

        self.cell_btns[cell_idx].label = cell_txt

    def uncover_bombs(self) -> None:
        """Uncover all bombs."""
        for btn, txt in zip(self.cell_btns, self.cells_txt):
            if txt == BOMB_CHAR:
                btn.label = BOMB_CHAR

    def uncover_adjacent(self, cell_idx: int) -> None:
        """Uncover adjacent cells if all bombs have been identified."""
        try:
            expected_bombs = int(self.cell_btns[cell_idx].label)
        except ValueError:
            return

        seen_bombs = sum(
            1
            for adj_idx in adjacent_idxs(cell_idx)
            if self.cell_btns[adj_idx].label == FLAG_CHAR
        )

        if expected_bombs == seen_bombs:
            for adj_idx in adjacent_idxs(cell_idx):
                self.uncover_cell(adj_idx)

    def flag_cell(self, cell_idx: int) -> None:
        """Flag a cell where the player thinks is a bomb."""
        cell = self.cell_btns[cell_idx]

        if cell.label not in ["", FLAG_CHAR]:
            # only flag untouched cells
            return

        cell.label = FLAG_CHAR if cell.label == "" else ""


class SweptApp(App):
    """The game application."""

    async def on_mount(self) -> None:
        await self.view.dock(Swept())


if __name__ == "__main__":
    SweptApp.run(log="textual.log")
