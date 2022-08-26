import enum


class GameStatus(enum.Enum):
    IN_PROGRESS = enum.auto()
    WON = enum.auto()
    LOST = enum.auto()
