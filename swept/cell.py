import textual.events as events
from textual.widgets import Button, ButtonPressed


class LeftClick(ButtonPressed):
    pass


class RightClick(ButtonPressed):
    pass


class MiddleClick(ButtonPressed):
    pass


class Cell(Button):
    """Exactly like button, but differentiate between right, left, and middle click."""

    async def on_click(self, event: events.Click) -> None:
        event.prevent_default().stop()

        if event.button == 1:
            await self.emit(LeftClick(self))
        elif event.button == 2:
            await self.emit(MiddleClick(self))
        elif event.button == 3:
            await self.emit(RightClick(self))
