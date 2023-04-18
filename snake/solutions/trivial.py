import time

from snake.algorithms.hamiltonian import HamiltonianCycle
from snake.game import Direction, SnakeGame
from snake.solutions.base import BaseSolution


class TrivialSolution(BaseSolution):
    def run(self) -> SnakeGame:
        hc = HamiltonianCycle((self.game.width, self.game.height))

        # FIND INITIAL CYCLE INDEX
        for i, pos in enumerate(hc.cycle):
            if pos == self.game.snake.head.get_position():
                cycle_idx = i
                break
        else:
            raise ValueError("Snake head not in cycle")

        while True:
            head_pos, tail_pos = self.game.snake.head.get_position(), self.game.snake.tail.get_position()
            food_pos = self.game.food_pos
            # MOVE SNAKE HEAD TO NEXT POSITION IN CYCLE
            next_idx = (cycle_idx + 1) % len(hc.cycle)
            next_pos = hc.cycle[next_idx]
            for action in Direction:
                if self.game.potential_position(action) == next_pos:
                    break
            else:
                raise ValueError(f"Cannot find action that leads to next position from {head_pos} to {next_pos}")
            cycle_idx = next_idx

            # DISPLAY STUFFS
            if self.to_print:
                hc.visualize_cycle()

                print(self.game.board)
                print("\n\n\n")

                print("HEAD", (head_pos[1], head_pos[0]), hc.get_position_order(head_pos))
                print("TAIL", (tail_pos[1], tail_pos[0]), hc.get_position_order(tail_pos))
                print("FOOD", (food_pos[1], food_pos[0]), hc.get_position_order(food_pos))

                self.game.display()
                print(f"ACITON: {action}")
                time.sleep(self.frame_period)

            if self.game.make_move(action):
                break

        return self.game
