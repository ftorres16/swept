from textual.app import App
from textual.reactive import Reactive

from swept.cell import LeftClick, MiddleClick, RightClick
from swept.cell_grid import CellGrid
from swept.enums import GameStatus
from swept.help_panel import HelpPanel
from swept.top_panel import TopPanel, TopPanelPressed


class SweptApp(App):
    """The game application."""

    game_status = Reactive(GameStatus.IN_PROGRESS)

    def watch_game_status(self, game_status: GameStatus) -> None:
        """Control game status."""
        self.cell_grid.game_status = self.game_status
        self.title_bar.game_status = self.game_status

    async def on_load(self, event):
        await self.bind("q", "quit", "Quit")
        await self.bind("r", "reset", "Reset")

    async def on_mount(self) -> None:
        self.title_bar = TopPanel()
        self.cell_grid = CellGrid()
        self.help_panel = HelpPanel()

        await self.view.dock(self.title_bar, size=3, edge="top")
        await self.view.dock(self.help_panel, size=40, edge="right")
        await self.view.dock(
            self.help_panel, size=40, edge="left"
        )  # workaround to center grid
        await self.view.dock(self.cell_grid, edge="top")

    def handle_top_panel_pressed(self, message: TopPanelPressed) -> None:
        self.game_status = GameStatus.IN_PROGRESS
        self.cell_grid.reset_game()

    def handle_left_click(self, message: LeftClick) -> None:
        """Left click on a cell in the grid."""
        if self.game_status != GameStatus.IN_PROGRESS:
            return
        self.cell_grid.uncover_cell(int(message.sender.name))

        if self.cell_grid.win_condition():
            self.game_status = GameStatus.WON
        elif self.cell_grid.lose_condition():
            self.game_status = GameStatus.LOST

    def handle_middle_click(self, message: MiddleClick) -> None:
        """Middle click on a cell in the grid."""
        if self.game_status != GameStatus.IN_PROGRESS:
            return
        self.cell_grid.uncover_adjacent(int(message.sender.name))

        if self.cell_grid.win_condition():
            self.game_status = GameStatus.WON
        elif self.cell_grid.lose_condition():
            self.game_status = GameStatus.LOST

    def handle_right_click(self, message: RightClick) -> None:
        """Right click on a cell in the grid."""
        if self.game_status != GameStatus.IN_PROGRESS:
            return
        self.cell_grid.flag_cell(int(message.sender.name))

        if self.cell_grid.win_condition():
            self.game_status = GameStatus.WON
        elif self.cell_grid.lose_condition():
            self.game_status = GameStatus.LOST

    async def action_reset(self) -> None:
        self.game_status = GameStatus.IN_PROGRESS
        self.cell_grid.reset_game()


if __name__ == "__main__":
    SweptApp.run(log="textual.log")
