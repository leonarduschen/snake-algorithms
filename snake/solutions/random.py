import random
import time
from typing import Tuple

from snake.algorithms.hamiltonian import HamiltonianCycle
from snake.game import Direction, SnakeGame
from snake.solutions.base import BaseSolution

random.seed(10)


def not_overtake_tail(
    pos: Tuple[int, int], head: Tuple[int, int], tail: Tuple[int, int], hc: HamiltonianCycle, room_left: int
) -> bool:
    head_order, tail_order = hc.get_position_order(head), hc.get_position_order(tail)
    pos_order = hc.get_position_order(pos)
    n = hc.size[0] * hc.size[1]

    if head_order == tail_order:
        return True
    elif head_order > tail_order:
        if not (tail_order <= pos_order <= head_order):
            if pos_order < tail_order:
                room = tail_order - pos_order
            else:
                room = tail_order + n - pos_order
            if room >= room_left:
                return True
        return False
    else:
        if head_order < pos_order < tail_order:
            room = tail_order - pos_order
            if room >= room_left:
                return True
        return False


def positive_move(pos: Tuple[int, int], head: Tuple[int, int], hc: HamiltonianCycle) -> bool:
    # PREVENTS FROM HITTING BODY
    head_order = hc.get_position_order(head)
    pos_order = hc.get_position_order(pos)
    n = hc.size[0] * hc.size[1]

    if head_order == n - 1:
        return pos_order == 0

    return pos_order > head_order


def get_shortcut_gained(
    pos: Tuple[int, int],
    food: Tuple[int, int],
    head: Tuple[int, int],
    tail: Tuple[int, int],
    hc: HamiltonianCycle,
) -> int:
    head_order, _ = hc.get_position_order(head), hc.get_position_order(tail)
    pos_order = hc.get_position_order(pos)
    food_order = hc.get_position_order(food)
    n = hc.size[0] * hc.size[1]

    # CALCULATE CURRENT DISTANCE IN HC ORDER
    if head_order > food_order:
        cur_distance = food_order - head_order + n
    else:
        cur_distance = food_order - head_order

    # CALCULATE FUTURE DISTANCE IN HC ORDER
    if pos_order > food_order:
        potential_distance = food_order - pos_order + n
    else:
        potential_distance = food_order - pos_order

    # print(f"head, pos, food: {head_order}-{pos_order}-{food_order}")
    # print(f"Found shortcut: {pos}:{pos_order} - pot_distance: {potential_distance} - cur distance: {cur_distance}")
    return -(potential_distance - cur_distance)


def not_overtake_food(
    pos: Tuple[int, int],
    food: Tuple[int, int],
    head: Tuple[int, int],
    tail: Tuple[int, int],
    hc: HamiltonianCycle,
) -> int:
    shortcut_gained = get_shortcut_gained(pos, food, head, tail, hc)
    return shortcut_gained > 0


class RandomSolution(BaseSolution):
    def __init__(self, game: SnakeGame, to_print: bool, frame_period: float, room_left: int, length_cutoff: float):
        self.room_left = room_left
        self.length_cutoff = length_cutoff

        super().__init__(game, to_print, frame_period)

    def run(self) -> SnakeGame:
        hc = HamiltonianCycle((self.game.width, self.game.height))

        while True:
            # MOVE SNAKE HEAD TO NEXT RANDOM POSITION
            potential_directions = [Direction.UP, Direction.RIGHT, Direction.DOWN, Direction.LEFT]
            random.shuffle(potential_directions)

            valid_directions = [direction for direction in potential_directions if self.game.check_valid(direction)]
            head_pos = self.game.snake.head.get_position()
            tail_pos = self.game.snake.tail.get_position()
            food_pos = self.game.food_pos

            for direction in valid_directions:
                if self.game.length > self.game.max_length * self.length_cutoff:
                    continue
                # CHECK FOR VALID ORDERING WHEN LENGTH >= 2 (POSSIBLE TO GET STUCK)
                if self.game.length >= 2:
                    # CHECK IF POSITION HAS HAMILTONIAN CYCLE ORDERING
                    position = self.game.potential_position(direction)
                    if not not_overtake_tail(
                        position,
                        head_pos,
                        tail_pos,
                        hc,
                        self.room_left,
                    ):
                        continue

                    if not positive_move(position, head_pos, hc):
                        continue
                    if not not_overtake_food(position, food_pos, head_pos, tail_pos, hc):
                        continue

                # DIRECTION FOUND
                break
            else:
                # NO GOOD SHORTCUT OR LENGTH TOO LONG, MOVE NORMALLY THROUGH HAMILTONIAN CYCLE
                head_order = hc.get_position_order(head_pos)
                next_pos = hc.cycle[(head_order + 1) % len(hc.cycle)]
                for direction in valid_directions:
                    if self.game.potential_position(direction) == next_pos:
                        # DIRECTION FOUND
                        break

            # DISPLAY STUFFS
            if self.to_print:
                hc.visualize_cycle()

                print(self.game.board)
                print("\n\n\n")

                print("HEAD", (head_pos[1], head_pos[0]), hc.get_position_order(head_pos))
                print("TAIL", (tail_pos[1], tail_pos[0]), hc.get_position_order(tail_pos))
                print("FOOD", (food_pos[1], food_pos[0]), hc.get_position_order(food_pos))

                self.game.display()
                print(f"ACITON: {direction}")
                time.sleep(self.frame_period)

            if self.game.make_move(direction):
                break

        return self.game
