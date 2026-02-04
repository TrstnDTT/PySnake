import pygame
import random
from snake import Snake
from food import Food
from settings import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    INITIAL_MOVE_INTERVAL,
    SPEED_UP_FACTOR,
    CELL_SIZE,
    WHITE,
    FOOD_COUNT,
    OBSTACLE_COUNT,
    OBSTACLE_COLOR,
)

class Game:
    def __init__(self):
        self.font = pygame.font.SysFont(None, 36)
        self.large_font = pygame.font.SysFont(None, 72)
        self.reset()

    def reset(self):
        start_x = (WINDOW_WIDTH // 2) // CELL_SIZE * CELL_SIZE
        start_y = (WINDOW_HEIGHT // 2) // CELL_SIZE * CELL_SIZE
        self.snake = Snake(start_x, start_y)
        self._spawn_obstacles()
        self.foods = [Food() for _ in range(FOOD_COUNT)]
        self._respawn_all_foods()
        self.alive = True
        self.move_interval = INITIAL_MOVE_INTERVAL
        self.accumulator = 0.0
        self.score = 0

    def _spawn_obstacles(self):
        self.obstacles = []
        max_cols = WINDOW_WIDTH // CELL_SIZE
        max_rows = WINDOW_HEIGHT // CELL_SIZE
        occupied = {(self.snake.x, self.snake.y)}
        if OBSTACLE_COUNT <= 0:
            return

        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        start_col = random.randint(0, max_cols - 1)
        start_row = random.randint(0, max_rows - 1)
        start = (start_col * CELL_SIZE, start_row * CELL_SIZE)
        while start in occupied:
            start_col = random.randint(0, max_cols - 1)
            start_row = random.randint(0, max_rows - 1)
            start = (start_col * CELL_SIZE, start_row * CELL_SIZE)

        self.obstacles.append(start)
        occupied.add(start)
        current = start

        for _ in range(OBSTACLE_COUNT - 1):
            if random.random() < 0.25:
                current = random.choice(self.obstacles)

            placed = False
            for _ in range(8):
                dx, dy = random.choice(directions)
                next_pos = (current[0] + dx * CELL_SIZE, current[1] + dy * CELL_SIZE)
                if (next_pos[0] < 0 or next_pos[0] >= WINDOW_WIDTH or
                        next_pos[1] < 0 or next_pos[1] >= WINDOW_HEIGHT):
                    continue
                if next_pos in occupied:
                    continue
                self.obstacles.append(next_pos)
                occupied.add(next_pos)
                current = next_pos
                placed = True
                break

            if not placed:
                current = random.choice(self.obstacles)

    def _respawn_all_foods(self):
        occupied = [(self.snake.x, self.snake.y)] + self.obstacles
        for food in self.foods:
            food.respawn(occupied)
            occupied.append(food.position)

    def _add_obstacles(self, count=1):
        max_cols = WINDOW_WIDTH // CELL_SIZE
        max_rows = WINDOW_HEIGHT // CELL_SIZE
        occupied = {(self.snake.x, self.snake.y)}
        for food in self.foods:
            occupied.add(food.position)
        for pos in self.obstacles:
            occupied.add(pos)
        for _ in range(count):
            # Spawn new obstacles anywhere on the grid (not necessarily connected)
            for _ in range(200):
                x = random.randint(0, max_cols - 1) * CELL_SIZE
                y = random.randint(0, max_rows - 1) * CELL_SIZE
                if (x, y) not in occupied:
                    self.obstacles.append((x, y))
                    occupied.add((x, y))
                    break
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if not self.alive and event.key == pygame.K_r:
                self.reset()
                return
            if event.key == pygame.K_UP:
                self.snake.change_direction("UP")
            elif event.key == pygame.K_DOWN:
                self.snake.change_direction("DOWN")
            elif event.key == pygame.K_LEFT:
                self.snake.change_direction("LEFT")
            elif event.key == pygame.K_RIGHT:
                self.snake.change_direction("RIGHT")
    
    def update(self, dt):
        if not self.alive:
            return
        
        self.accumulator += dt
        while self.accumulator >= self.move_interval:
            self.snake.move()
            self.accumulator -= self.move_interval
    
        if (self.snake.x < 0 or
                self.snake.x + self.snake.size > WINDOW_WIDTH or
                self.snake.y < 0 or
                self.snake.y + self.snake.size > WINDOW_HEIGHT):
                self.alive = False

        if (self.snake.x, self.snake.y) in self.obstacles:
                self.alive = False

        for food in self.foods:
            if (self.snake.x, self.snake.y) == food.position:
                occupied = [(self.snake.x, self.snake.y)]
                for other in self.foods:
                    if other is not food:
                        occupied.append(other.position)
                food.respawn(occupied)
                self.move_interval *= SPEED_UP_FACTOR
                self.score += 100
                self._add_obstacles(1)
                break

    def draw(self, screen):
        alpha = 1.0
        if self.move_interval > 0:
            alpha = max(0.0, min(1.0, self.accumulator / self.move_interval))
        self.snake.draw(screen, alpha)
        for food in self.foods:
            food.draw(screen)
        for obstacle in self.obstacles:
            pygame.draw.rect(
                screen,
                OBSTACLE_COLOR,
                (*obstacle, CELL_SIZE, CELL_SIZE)
            )
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(
            score_text,
            (WINDOW_WIDTH - score_text.get_width() - 10, 10)
        )
        if not self.alive:
            game_over = self.large_font.render("GAME OVER", True, WHITE)
            restart = self.font.render("Press R to restart", True, WHITE)
            screen.blit(
                game_over,
                (WINDOW_WIDTH // 2 - game_over.get_width() // 2,
                 WINDOW_HEIGHT // 2 - game_over.get_height() // 2)
            )
            screen.blit(
                restart,
                (WINDOW_WIDTH // 2 - restart.get_width() // 2,
                 WINDOW_HEIGHT // 2 + game_over.get_height() // 2 + 10)
            )
