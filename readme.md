# PySnake

A fast, grid-based Snake game built with Pygame. It includes multiple foods, combo scoring, power-ups, obstacles that grow over time, smooth interpolated animation, and lightweight procedural sound effects with juicy visuals.

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
- The snake speeds up after each food and grows.
- Combos increase your score multiplier if you chain pickups quickly.
- Power-ups can slow time or double your score temporarily.
- Obstacles spawn on the grid and end the game on contact (and keep growing).
- Walls (screen edges) also end the game.

## Tuning

Edit `src/settings.py`:

- `INITIAL_MOVE_INTERVAL`: base speed (lower is faster)
- `SPEED_UP_FACTOR`: how much speed increases per food
- `FOOD_COUNT`: number of food tiles
- `OBSTACLE_COUNT`: initial obstacle count
- `POWERUP_SPAWN_CHANCE`: chance to spawn a power-up on food pickup
- `POWERUP_DURATION`: how long power-ups last
- `COMBO_WINDOW`: seconds allowed between foods to keep a combo
- `CELL_SIZE`: grid size

## Notes

- The snake moves on a grid for consistent collisions.
- Rendering is smoothly interpolated between grid steps for fluid motion.
