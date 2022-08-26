from rich.align import Align
from rich.panel import Panel
from textual.events import Click
from textual.message import Message
from textual.reactive import Reactive
from textual.widget import Widget

from swept.enums import GameStatus


STATUS_EMOJIS = {
    GameStatus.WON: ":sunglasses:",
    GameStatus.LOST: ":dizzy_face:",
    GameStatus.IN_PROGRESS: ":slightly_smiling_face:",
}


class TopPanelPressed(Message, bubble=True):
    pass


class TopPanel(Widget):
    game_status = Reactive(GameStatus.IN_PROGRESS)

    def render(self) -> Panel:
        return Panel(Align(STATUS_EMOJIS[self.game_status], align="center"))

    async def on_click(self, event: Click) -> None:
        self.log("test!")
        event.prevent_default().stop()
        await self.emit(TopPanelPressed(self))
