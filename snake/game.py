from __future__ import annotations

import enum
import random
from typing import Optional, Tuple

import numpy as np

random.seed(10)


class Direction(enum.Enum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3


class BodyNode:
    def __init__(self, parent: Optional[BodyNode], x: int, y: int):
        self.parent = parent
        self.x = x
        self.y = y

    def set_x(self, x: int) -> None:
        self.x = x

    def set_y(self, y: int) -> None:
        self.y = y

    def set_parent(self, parent: BodyNode) -> None:
        self.parent = parent

    def get_position(self) -> Tuple[int, int]:
        return (self.x, self.y)

    def get_index(self) -> Tuple[int, int]:
        return (self.y, self.x)


class Snake:
    def __init__(self, x: int, y: int):
        self.head = BodyNode(None, x, y)
        self.tail = self.head

    def move_body_foward(self) -> None:
        current_node = self.tail
        while current_node.parent is not None:
            parentPosition = current_node.parent.get_position()
            current_node.set_x(parentPosition[0])
            current_node.set_y(parentPosition[1])
            current_node = current_node.parent

    def move(self, direction: Direction) -> Tuple[int, int, int, int]:
        (old_tail_x, old_tail_y) = self.tail.get_position()
        self.move_body_foward()
        head_position = self.head.get_position()
        if direction == Direction.UP:
            self.head.set_y(head_position[1] - 1)
        elif direction == Direction.RIGHT:
            self.head.set_x(head_position[0] + 1)
        elif direction == Direction.DOWN:
            self.head.set_y(head_position[1] + 1)
        elif direction == Direction.LEFT:
            self.head.set_x(head_position[0] - 1)
        return (old_tail_x, old_tail_y, *self.head.get_position())

    def new_head(self, new_x: int, new_y: int):
        new_head = BodyNode(None, new_x, new_y)
        self.head.set_parent(new_head)
        self.head = new_head

    def get_head(self) -> BodyNode:
        return self.head

    def get_tail(self) -> BodyNode:
        return self.tail


class SnakeGame:
    def __init__(self, width: int, height: int, starting_food: bool = False):
        # arbitrary numbers to signify head, body, and food)
        # 0 for empty space
        self.head_val = 5
        self.body_val = 1
        self.food_val = 9
        self.width = width
        self.height = height
        self.board = np.zeros([height, width], dtype=int)

        self.length = 1

        start_x = width // 2
        start_y = height // 2

        self.board[start_x, start_y] = self.head_val
        self.snake = Snake(start_x, start_y)

        if starting_food:
            self.initial_spawn_food()
            self.make_move(Direction.DOWN)
        else:
            self.spawn_food()

        self.max_length = width * height - 1
        self.move_count = 0

    def initial_spawn_food(self) -> None:
        self.food_index = self.snake.head.get_position()[0] + 1, self.snake.head.get_position()[1]
        self.board[self.food_index] = self.food_val

    def spawn_food(self) -> None:
        # spawn food at location not occupied by snake
        empty_cells = []
        for index, value in np.ndenumerate(self.board):
            if value != self.body_val and value != self.head_val:
                empty_cells.append(index)
        self.food_index = random.choice(empty_cells)  # type: ignore
        self.food_pos = self.food_index[1], self.food_index[0]
        self.board[self.food_index] = self.food_val

    def check_valid(self, direction: Direction):
        # check if move is blocked by wall
        new_x, new_y = self.potential_position(direction)
        if new_x == -1 or new_x == self.width:
            return False
        if new_y == -1 or new_y == self.height:
            return False

        # check if move is blocked by snake body
        if self.board[new_y, new_x] == self.body_val:
            # IF BLOCKED BY TAIL AND LENGTH > 2, THEN TAIL WILL MOVE OUT OF THE WAY AND IT IS FINE
            if (new_x, new_y) == self.snake.tail.get_position() and self.length > 2:
                return True
            return False
        return True

    def potential_position(self, direction: Direction):
        (new_x, new_y) = self.snake.get_head().get_position()
        if direction == Direction.UP:
            new_y -= 1
        elif direction == Direction.RIGHT:
            new_x += 1
        elif direction == Direction.DOWN:
            new_y += 1
        elif direction == Direction.LEFT:
            new_x -= 1
        return (new_x, new_y)

    def display(self):
        for i in range(self.width + 2):
            print("-", end="")
        for i in range(self.height):
            print("\n|", end="")
            for j in range(self.width):
                if self.board[i, j] == 0:
                    print(" ", end="")
                elif self.board[i, j] == self.head_val:
                    print("O", end="")
                elif self.board[i, j] == self.body_val:
                    print("X", end="")
                elif self.board[i, j] == self.food_val:
                    print("*", end="")
            print("|", end="")
        print()
        for i in range(self.width + 2):
            print("-", end="")
        print()

    def make_move(self, direction: Direction):
        game_over = False
        if self.check_valid(direction):
            (head_x, head_y) = self.snake.get_head().get_position()
            # set old head to body val
            self.board[head_y, head_x] = self.body_val

            # check if we got the fruit
            potX, potY = self.potential_position(direction)
            if self.board[potY, potX] == self.food_val:
                # extend the snake
                self.snake.new_head(potX, potY)
                self.board[potY, potX] = self.head_val
                self.spawn_food()
                self.length += 1
            else:
                # move the snake
                (old_tail_x, old_tail_y, new_head_x, new_head_y) = self.snake.move(direction)
                self.board[old_tail_y, old_tail_x] = 0
                self.board[new_head_y, new_head_x] = self.head_val
        else:
            game_over = True

        if self.length == self.max_length:
            game_over = True

        self.move_count += 1

        return game_over
