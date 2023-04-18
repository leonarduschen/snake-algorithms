from snake.game import Direction, SnakeGame


def main() -> None:
    game = SnakeGame(8, 8)
    game.display()
    while True:
        direction = input("Input Direction (w,a,s,d or q to quit): ")
        if direction == "w":
            game_over = game.make_move(Direction.UP)
        elif direction == "a":
            game_over = game.make_move(Direction.LEFT)
        elif direction == "s":
            game_over = game.make_move(Direction.DOWN)
        elif direction == "d":
            game_over = game.make_move(Direction.RIGHT)
        elif direction == "q":
            break
        if game_over:
            print(f"Game over, length: {game.length}")
            break
        else:
            game.display()
            print(f"Length {game.length}")


if __name__ == "__main__":
    main()
