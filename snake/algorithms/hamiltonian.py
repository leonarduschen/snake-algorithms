from typing import Dict, List, Optional, Tuple


class HamiltonianCycle:
    def __init__(self, size: Tuple[int, int]):
        self.size = size
        self.cycle = self._init_cycle()
        self.position_map = self._init_position_map()

    def _init_cycle(self) -> List[Tuple[int, int]]:
        path: List[Tuple[int, int]] = [(0, i) for i in range(self.size[1])]  # STRAIGHT +1 PATH ON AXIS 1
        path.append((1, path[-1][1]))

        cur = path[-1]
        axis0_move = 1
        axis1_move = -1
        while len(path) < self.size[0] * self.size[1]:
            if 1 <= cur[0] + axis0_move < self.size[0]:
                new = cur[0] + axis0_move, cur[1]
            else:
                new = cur[0], cur[1] + axis1_move
                axis0_move = -1 if axis0_move == 1 else 1
            path.append(new)
            cur = new

        return path

    def _init_position_map(self) -> Dict[Tuple[int, int], int]:
        mapping = {}
        for i, pos in enumerate(self.cycle):
            mapping[pos] = i
        return mapping

    def get_position_order(self, pos: Tuple[int, int]) -> int:
        return self.position_map[pos]

    def visualize_cycle(self) -> None:
        mat: List[List[Optional[int]]] = [[None for _ in range(self.size[0])] for _ in range(self.size[1])]
        for i, pos in enumerate(self.cycle):
            mat[pos[1]][pos[0]] = i

        print("Hamiltonian Cycle: \n")
        for row in mat:
            print([str(num).zfill(2) for num in row])
        print("\n\n\n")
