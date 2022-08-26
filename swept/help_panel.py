from rich.panel import Panel
from textual.widget import Widget


class HelpPanel(Widget):
    def render(self) -> Panel:
        return Panel(
            (
                "Left click on the cells to uncover what's underneath."
                "\n Cells with numbers show how many bombs are adjacent."
                "\n Right click on a cell to mark that there's a bomb underneath."
                "\n Game is won when all cells are uncovered or flagged."
                "\n Game is lost when you uncover a bomb and it explodes."
                "\n\n # Shortcuts"
                "\n R - restart game"
                "\n Q - quit game"
            ),
            title="Help",
        )
