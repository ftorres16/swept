from textual.app import App

from swept.cell_grid import CellGrid
from swept.help_panel import HelpPanel
from swept.top_panel import TopPanel, TopPanelPressed


class SweptApp(App):
    """The game application."""

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
        self.cell_grid.reset_game()

    async def action_reset(self) -> None:
        self.cell_grid.reset_game()


if __name__ == "__main__":
    SweptApp.run(log="textual.log")
