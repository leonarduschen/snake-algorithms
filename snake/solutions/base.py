from abc import ABC, abstractmethod

from snake.game import SnakeGame


class BaseSolution(ABC):
    def __init__(self, game: SnakeGame, to_print: bool, frame_period: float):
        self.game = game
        self.to_print = to_print
        self.frame_period = frame_period

    @abstractmethod
    def run(self) -> SnakeGame:
        ...
