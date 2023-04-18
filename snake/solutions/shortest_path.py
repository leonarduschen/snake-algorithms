import time
from typing import Dict, List, Tuple

from snake.algorithms.djikstra import Graph, find_shortest_path  # type: ignore
from snake.algorithms.hamiltonian import HamiltonianCycle
from snake.game import Direction, SnakeGame
from snake.solutions.base import BaseSolution

SHORTCUT_GAIN_CUTOFF = 10


def convert_to_graph_dict(board: List[List[int]]) -> Dict[Tuple[int, int], Dict[Tuple[int, int], int]]:
    n, m = len(board), len(board[0])

    # INITIALIZE EMPTY GRAPH DICT
    # INDEX IS SWITCHED BECAUSE WE WANT TO STORE POSITIONS INSTEAD OF BOARD INDICES
    gd: Dict[Tuple[int, int], Dict[Tuple[int, int], int]] = {}
    for i in range(n):
        for j in range(m):
            gd[(j, i)] = {}

    for i in range(n):
        for j in range(m):
            y, x = i, j

            if board[y][x] != 0:
                continue

            deltas = [(0, 1), (0, -1), (1, 0), (-1, 0)]
            for delta_y, delta_x in deltas:
                new_y = y + delta_y
                new_x = x + delta_x

                if 0 <= new_y < n and 0 <= new_x < m:
                    value = board[new_y][new_x]
                    if value == 0:
                        gd[(x, y)][(new_x, new_y)] = 1

    # for source, dests in gd.items():
    #     for dest, distance in dests.items():
    #         print(source, dest, distance)

    return gd


def is_valid_order(
    pos: Tuple[int, int],
    head: Tuple[int, int],
    tail: Tuple[int, int],
    hc: HamiltonianCycle,
    room_left: int,
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


def prepare_graph(
    board: List[List[int]],
    head: Tuple[int, int],
    tail: Tuple[int, int],
    food: Tuple[int, int],
    hc: HamiltonianCycle,
) -> Graph:
    # HEAD AND FOOD AS 0s
    board[head[1]][head[0]] = 0
    board[food[1]][food[0]] = 0

    # INVALID ORDERING AS 3s AND 4s
    n, m = len(board), len(board[0])
    head_order, tail_order = hc.get_position_order(head), hc.get_position_order(tail)
    food_order = hc.get_position_order(food)

    # CANNOT OVERTAKE TAIL
    for i in range(n):
        for j in range(m):
            if board[i][j] == 0:
                y, x = i, j
                order = hc.get_position_order((x, y))
                if head_order == tail_order:
                    ...
                elif head_order > tail_order:
                    if tail_order < order < head_order:
                        # print("HERE", head_order, tail_order, order)
                        board[i][j] = 3
                else:
                    if not (head_order <= order <= tail_order):
                        # print("HOHO", head_order, tail_order, order)
                        board[i][j] = 3

    # CANNOT OVERTAKE FOOD
    for i in range(n):
        for j in range(m):
            if board[i][j] == 0:
                y, x = i, j
                order = hc.get_position_order((x, y))
                if head_order < food_order:
                    if order < head_order or order > food_order:
                        board[i][j] = 4
                else:
                    if food_order < order < head_order:
                        board[i][j] = 4

    # print(board)
    gd = convert_to_graph_dict(board)
    nodes = [key for key in gd.keys()]
    graph = Graph(nodes, gd)
    return graph


class ShortestPathSolution(BaseSolution):
    def __init__(self, game: SnakeGame, to_print: bool, frame_period: float, length_cutoff: float):
        self.length_cutoff = length_cutoff

        super().__init__(game, to_print, frame_period)

    def run(self) -> SnakeGame:
        hc = HamiltonianCycle((self.game.width, self.game.height))

        shortest_path: List[Tuple[int, int]] = []
        while True:
            # INITIALIZE VARS
            head_pos, tail_pos = self.game.snake.head.get_position(), self.game.snake.tail.get_position()
            food_pos = self.game.food_pos

            # RENEW SHORTEST PATH WHEN FOOD IS REACHED
            if len(shortest_path) == 0:
                if self.game.length > self.game.max_length * self.length_cutoff:
                    if self.to_print:
                        print("NOT ATTEMPTING TO FIND SHORTEST PATH")
                else:
                    # PREPARE GRAPH
                    graph = prepare_graph(self.game.board.copy(), head_pos, tail_pos, food_pos, hc)  # type: ignore

                    # FIND SHORTEST PATH
                    try:
                        shortest_path = find_shortest_path(graph, head_pos, food_pos)
                        print(shortest_path)
                    except KeyError:
                        if self.to_print:
                            print("CANT FIND VALID SHORTEST PATH")
                    else:
                        shortest_path.pop(0)
                        if self.to_print:
                            print("NEW SHORTEST PATH:", shortest_path)

            if len(shortest_path) > 0:
                # SHORTEST PATH IS FOUND, MOVE TO POSITIONS IN PATH
                potential_directions = [Direction.UP, Direction.RIGHT, Direction.DOWN, Direction.LEFT]
                for direction in potential_directions:
                    if self.game.potential_position(direction) == shortest_path[0]:
                        shortest_path.pop(0)
                        break
                else:
                    raise ValueError("Unable to find direction to next position in shortest path")
            else:
                # NO GOOD SHORTCUT, MOVE NORMALLY THROUGH HAMILTONIAN CYCLE
                potential_directions = [Direction.UP, Direction.RIGHT, Direction.DOWN, Direction.LEFT]
                valid_directions = [direction for direction in potential_directions if self.game.check_valid(direction)]

                head_pos = self.game.snake.head.get_position()
                head_order = hc.get_position_order(head_pos)
                next_pos = hc.cycle[(head_order + 1) % len(hc.cycle)]
                for direction in valid_directions:
                    if self.game.potential_position(direction) == next_pos:
                        # DIRECTION FOUND
                        break
                else:
                    if self.to_print:
                        print("DIR NOT FOUND")

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
                print("\n\n\n-------\n\n\n")

            if self.game.make_move(direction):
                # print(self.game.length, self.game.move_count)
                # self.game.display()
                break

        return self.game
