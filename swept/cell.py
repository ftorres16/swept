import enum

import textual.events as events
from textual.reactive import Reactive
from textual.widgets import Button, ButtonPressed

from swept.exceptions import CantToggleFlag, CantUncover

BOMB_CHAR = ":bomb:"
FLAG_CHAR = ":triangular_flag:"


class CellStatus(enum.Enum):
    COVERED = enum.auto()
    FLAGGED = enum.auto()
    UNCOVERED = enum.auto()
    EXPLODED = enum.auto()
    FLAGGED_WON = enum.auto()  # set this state when the game is won


class LeftClick(ButtonPressed):
    pass


class RightClick(ButtonPressed):
    pass


class MiddleClick(ButtonPressed):
    pass


class Cell(Button):
    """Similar to button, but differentiate between right, left, and middle click."""

    # styles
    COVERED_CELL = "rgb(112,128,144) on rgb(112,128,144)"
    UNCOVERED_CELL = "white on rgb(16,16,16)"
    EXPLODED_CELL = "white on red"
    WON_CELL = "white on green"

    status = Reactive(CellStatus.COVERED)
    value = Reactive("")

    def watch_status(self, status: CellStatus) -> None:
        """Control cell label based on its status."""
        if status == CellStatus.COVERED:
            self.label = ""
        elif status == CellStatus.FLAGGED:
            self.label = FLAG_CHAR
        elif status == CellStatus.UNCOVERED:
            self.button_style = self.UNCOVERED_CELL
            self.label = self.value if self.value != "0" else ""
        elif status == CellStatus.EXPLODED:
            self.button_style = self.EXPLODED_CELL
            self.label = self.value
        elif status == CellStatus.FLAGGED_WON:
            self.button_style = self.WON_CELL

    async def on_click(self, event: events.Click) -> None:
        event.prevent_default().stop()

        if event.button == 1:
            await self.emit(LeftClick(self))
        elif event.button == 2:
            await self.emit(MiddleClick(self))
        elif event.button == 3:
            await self.emit(RightClick(self))

    def uncover(self) -> None:
        if self.status != CellStatus.COVERED:
            raise CantUncover(
                f"Attempting to uncover cell from the wrong state. ({self.status=})"
            )

        self.status = (
            CellStatus.UNCOVERED if self.value != BOMB_CHAR else CellStatus.EXPLODED
        )

    def toggle_flag(self) -> None:
        """Attempt to toggle flag on a cell."""
        if self.status not in [CellStatus.COVERED, CellStatus.FLAGGED]:
            raise CantToggleFlag(
                f"Attempting to toggle cell flag from the wrong state. ({self.status=})"
            )

        self.status = (
            CellStatus.FLAGGED
            if self.status == CellStatus.COVERED
            else CellStatus.COVERED
        )
