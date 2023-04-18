import sys
from typing import Any, Dict, List, Type

from snake.game import SnakeGame
from snake.solutions.base import BaseSolution
from snake.solutions.greedy import GreedySolution
from snake.solutions.random import RandomSolution
from snake.solutions.shortest_path import ShortestPathSolution
from snake.solutions.trivial import TrivialSolution

RUN_SIMULATIONS = 1
SIZE = 10, 10
TO_PRINT = True
FRAME_PERIOD = 0.05


def run_simulations(solution_class: Type[BaseSolution], params_list: List[Dict[str, Any]]) -> None:
    scores = []
    move_counts = []
    for i in range(RUN_SIMULATIONS):
        game = SnakeGame(SIZE[0], SIZE[1])

        # RUN SOLUTION
        params = params_list[i]
        solution = solution_class(game=game, to_print=TO_PRINT, frame_period=FRAME_PERIOD, **params)
        game = solution.run()

        # RETREIVE METRICS
        scores.append(game.length)
        move_counts.append(game.move_count)

    print(
        "Average score: {} - Average move count: {}".format(
            sum(scores) / RUN_SIMULATIONS,
            sum(move_counts) / RUN_SIMULATIONS,
        )
    )
    print(
        "Percenrage of perfect game {}".format(
            len([score for score in scores if score == SIZE[0] * SIZE[1] - 1]) / RUN_SIMULATIONS
        )
    )

    print(scores)


def main():
    # TRIVIAL SOLUTION
    if sys.argv[-1] == "trivial":
        param_list = [{} for _ in range(RUN_SIMULATIONS)]
        run_simulations(TrivialSolution, param_list)

    # RANDOM SOLUTION
    elif sys.argv[-1] == "random":
        param_list = [
            {
                "room_left": 0,
                "length_cutoff": 0.5,
            }
            for _ in range(RUN_SIMULATIONS)
        ]
        run_simulations(RandomSolution, param_list)

    # GREEDY SOLUTION
    elif sys.argv[-1] == "greedy":
        param_list = [
            {
                "room_left": 0,
                "shortcut_gain_cutoff": 2,
                "length_cutoff": 0.5,
            }
            for _ in range(RUN_SIMULATIONS)
        ]
        run_simulations(GreedySolution, param_list)

    # SHORTEST PATH SOLUTION
    elif sys.argv[-1] == "shortest_path":
        param_list = [
            {
                "length_cutoff": 0.6,
            }
            for _ in range(RUN_SIMULATIONS)
        ]
        run_simulations(ShortestPathSolution, param_list)
    else:
        raise ValueError("Must supply correct argument")


if __name__ == "__main__":
    main()
