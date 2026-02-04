# PySnake

A fast, grid-based Snake game built with Pygame. It includes multiple foods, score tracking, obstacles that grow over time, and a smooth interpolated animation.

## Requirements

- Python 3.x
- Pygame

## Run

From the project folder:

```bash
python src/main.py
```

## Controls

- Arrow Keys: move
- R: restart after Game Over

## Gameplay

- Each food is worth 100 points.
- The snake speeds up after each food.
- Obstacles spawn on the grid and end the game on contact.
- Walls (screen edges) also end the game.

## Tuning

Edit `src/settings.py`:

- `INITIAL_MOVE_INTERVAL`: base speed (lower is faster)
- `SPEED_UP_FACTOR`: how much speed increases per food
- `FOOD_COUNT`: number of food tiles
- `OBSTACLE_COUNT`: initial obstacle count
- `CELL_SIZE`: grid size

## Notes

- The snake moves on a grid for consistent collisions.
- Rendering is smoothly interpolated between grid steps for fluid motion.
