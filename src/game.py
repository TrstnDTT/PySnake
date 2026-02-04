import array
import math
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
    BG_COLOR,
    GRID_COLOR,
    FOOD_COLOR,
    POWERUP_COLOR,
    COMBO_COLOR,
    POWERUP_SPAWN_CHANCE,
    POWERUP_DURATION,
    POWERUP_SLOW_FACTOR,
    POWERUP_SCORE_MULTIPLIER,
    COMBO_WINDOW,
    BASE_SCORE,
    PARTICLE_COUNT,
    SHAKE_EAT,
    SHAKE_DEAD,
)

class Game:
    def __init__(self):
        self.font = pygame.font.SysFont(None, 36)
        self.large_font = pygame.font.SysFont(None, 72)
        self.small_font = pygame.font.SysFont(None, 24)
        self.background = self._build_background()
        self.sounds = self._build_sounds()
        self.reset()

    def reset(self):
        start_x = (WINDOW_WIDTH // 2) // CELL_SIZE * CELL_SIZE
        start_y = (WINDOW_HEIGHT // 2) // CELL_SIZE * CELL_SIZE
        self.snake = Snake(start_x, start_y)
        self._spawn_obstacles()
        self.foods = [Food() for _ in range(FOOD_COUNT)]
        self.powerups = []
        self._respawn_all_foods()
        self.alive = True
        self.move_interval = INITIAL_MOVE_INTERVAL
        self.accumulator = 0.0
        self.score = 0
        self.combo_timer = 0.0
        self.combo_count = 0
        self.score_multiplier = 1
        self.powerup_timer = 0.0
        self.active_powerup = None
        self.particles = []
        self.popups = []
        self.shake_time = 0.0
        self.shake_intensity = 0.0

    def _build_background(self):
        surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        surface.fill(BG_COLOR)
        for x in range(0, WINDOW_WIDTH, CELL_SIZE):
            pygame.draw.line(surface, GRID_COLOR, (x, 0), (x, WINDOW_HEIGHT))
        for y in range(0, WINDOW_HEIGHT, CELL_SIZE):
            pygame.draw.line(surface, GRID_COLOR, (0, y), (WINDOW_WIDTH, y))
        return surface

    def _build_sounds(self):
        if not pygame.mixer.get_init():
            return {}
        rate, size, channels = pygame.mixer.get_init()
        if abs(size) != 16:
            return {}

        def tone(freq, duration, volume):
            samples = int(rate * duration)
            buf = array.array("h")
            amplitude = int(volume * 32767)
            for i in range(samples):
                sample = int(amplitude * math.sin(2 * math.pi * freq * i / rate))
                buf.append(sample)
                if channels == 2:
                    buf.append(sample)
            return pygame.mixer.Sound(buffer=buf)

        return {
            "eat": tone(720, 0.08, 0.35),
            "powerup": tone(880, 0.12, 0.35),
            "dead": tone(220, 0.25, 0.5),
        }

    def _play_sound(self, key):
        sound = self.sounds.get(key)
        if sound:
            sound.play()

    def _spawn_obstacles(self):
        self.obstacles = []
        max_cols = WINDOW_WIDTH // CELL_SIZE
        max_rows = WINDOW_HEIGHT // CELL_SIZE
        occupied = set(self.snake.segments)
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
        occupied = list(self.snake.segments) + self.obstacles
        for powerup in self.powerups:
            occupied.append(powerup["position"])
        for food in self.foods:
            food.respawn(occupied)
            occupied.append(food.position)

    def _spawn_powerup(self):
        max_cols = WINDOW_WIDTH // CELL_SIZE
        max_rows = WINDOW_HEIGHT // CELL_SIZE
        occupied = set(self.snake.segments)
        for food in self.foods:
            occupied.add(food.position)
        for pos in self.obstacles:
            occupied.add(pos)
        for powerup in self.powerups:
            occupied.add(powerup["position"])

        for _ in range(200):
            x = random.randint(0, max_cols - 1) * CELL_SIZE
            y = random.randint(0, max_rows - 1) * CELL_SIZE
            if (x, y) not in occupied:
                kind = random.choice(["slow", "double"])
                self.powerups.append({"type": kind, "position": (x, y)})
                break

    def _maybe_spawn_powerup(self):
        if random.random() <= POWERUP_SPAWN_CHANCE:
            if len(self.powerups) < 1:
                self._spawn_powerup()

    def _add_particles(self, position, color, count=PARTICLE_COUNT):
        for _ in range(count):
            angle = random.random() * 6.283
            speed = random.uniform(40, 140)
            self.particles.append({
                "x": position[0] + CELL_SIZE / 2,
                "y": position[1] + CELL_SIZE / 2,
                "vx": speed * math.cos(angle),
                "vy": speed * math.sin(angle),
                "life": random.uniform(0.4, 0.9),
                "color": color,
                "size": random.randint(2, 4),
            })

    def _add_popup(self, text, position, color):
        self.popups.append({
            "text": text,
            "x": position[0] + CELL_SIZE / 2,
            "y": position[1] + CELL_SIZE / 2,
            "vy": -20,
            "life": 1.0,
            "color": color,
        })

    def _update_particles(self, dt):
        alive = []
        for p in self.particles:
            p["life"] -= dt
            if p["life"] <= 0:
                continue
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            alive.append(p)
        self.particles = alive

    def _update_popups(self, dt):
        alive = []
        for popup in self.popups:
            popup["life"] -= dt
            if popup["life"] <= 0:
                continue
            popup["y"] += popup["vy"] * dt
            alive.append(popup)
        self.popups = alive

    def _current_interval(self):
        if self.powerup_timer > 0 and self.active_powerup == "slow":
            return self.move_interval * POWERUP_SLOW_FACTOR
        return self.move_interval

    def _draw_glow(self, screen, position, color, size):
        glow_size = size * 2
        glow = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
        glow_color = (color[0], color[1], color[2], 90)
        pygame.draw.rect(
            glow,
            glow_color,
            (size // 2, size // 2, size, size),
            border_radius=4
        )
        screen.blit(
            glow,
            (position[0] - size // 2, position[1] - size // 2),
            special_flags=pygame.BLEND_RGBA_ADD
        )

    def _add_obstacles(self, count=1):
        max_cols = WINDOW_WIDTH // CELL_SIZE
        max_rows = WINDOW_HEIGHT // CELL_SIZE
        occupied = set(self.snake.segments)
        for food in self.foods:
            occupied.add(food.position)
        for powerup in self.powerups:
            occupied.add(powerup["position"])
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
        self._update_particles(dt)
        self._update_popups(dt)
        if self.shake_time > 0:
            self.shake_time = max(0.0, self.shake_time - dt)

        if self.combo_timer > 0:
            self.combo_timer = max(0.0, self.combo_timer - dt)
            if self.combo_timer == 0:
                self.combo_count = 0

        if self.powerup_timer > 0:
            self.powerup_timer = max(0.0, self.powerup_timer - dt)
            if self.powerup_timer == 0:
                self.active_powerup = None
                self.score_multiplier = 1

        if not self.alive:
            return

        interval = self._current_interval()
        self.accumulator += dt
        while self.accumulator >= interval:
            self.snake.move()
            self.accumulator -= interval

            if (self.snake.x < 0 or
                    self.snake.x + self.snake.size > WINDOW_WIDTH or
                    self.snake.y < 0 or
                    self.snake.y + self.snake.size > WINDOW_HEIGHT):
                self.alive = False

            if (self.snake.x, self.snake.y) in self.obstacles:
                self.alive = False

            if self.snake.is_self_collision():
                self.alive = False

            if not self.alive:
                self.shake_time = 0.25
                self.shake_intensity = SHAKE_DEAD
                self._play_sound("dead")
                break

            for powerup in list(self.powerups):
                if (self.snake.x, self.snake.y) == powerup["position"]:
                    self.powerups.remove(powerup)
                    self.active_powerup = powerup["type"]
                    self.powerup_timer = POWERUP_DURATION
                    if self.active_powerup == "double":
                        self.score_multiplier = POWERUP_SCORE_MULTIPLIER
                        self._add_popup("2X", powerup["position"], POWERUP_COLOR)
                    else:
                        self._add_popup("SLOW", powerup["position"], POWERUP_COLOR)
                    self._add_particles(powerup["position"], POWERUP_COLOR, 12)
                    self.shake_time = 0.1
                    self.shake_intensity = SHAKE_EAT
                    self._play_sound("powerup")
                    break

            for food in self.foods:
                if (self.snake.x, self.snake.y) == food.position:
                    occupied = list(self.snake.segments) + self.obstacles
                    for other in self.foods:
                        if other is not food:
                            occupied.append(other.position)
                    for powerup in self.powerups:
                        occupied.append(powerup["position"])
                    food.respawn(occupied)
                    self.snake.grow(1)
                    self.move_interval *= SPEED_UP_FACTOR
                    if self.combo_timer > 0:
                        self.combo_count += 1
                    else:
                        self.combo_count = 1
                    self.combo_timer = COMBO_WINDOW
                    points = BASE_SCORE * self.combo_count * self.score_multiplier
                    self.score += points
                    self._add_popup(f"+{points}", food.position, COMBO_COLOR)
                    self._add_particles(food.position, FOOD_COLOR)
                    self.shake_time = 0.12
                    self.shake_intensity = SHAKE_EAT
                    self._add_obstacles(1)
                    self._maybe_spawn_powerup()
                    self._play_sound("eat")
                    break

    def draw(self, screen):
        offset_x = 0
        offset_y = 0
        if self.shake_time > 0:
            offset_x = random.randint(-self.shake_intensity, self.shake_intensity)
            offset_y = random.randint(-self.shake_intensity, self.shake_intensity)

        screen.fill(BG_COLOR)
        screen.blit(self.background, (offset_x, offset_y))

        alpha = 1.0
        interval = self._current_interval()
        if interval > 0:
            alpha = max(0.0, min(1.0, self.accumulator / interval))

        for obstacle in self.obstacles:
            pygame.draw.rect(
                screen,
                OBSTACLE_COLOR,
                (obstacle[0] + offset_x, obstacle[1] + offset_y, CELL_SIZE, CELL_SIZE),
                border_radius=2
            )

        for food in self.foods:
            self._draw_glow(screen, (food.position[0] + offset_x, food.position[1] + offset_y), FOOD_COLOR, CELL_SIZE)
            food.draw(screen, (offset_x, offset_y))

        for powerup in self.powerups:
            self._draw_glow(screen, (powerup["position"][0] + offset_x, powerup["position"][1] + offset_y), POWERUP_COLOR, CELL_SIZE)
            pygame.draw.rect(
                screen,
                POWERUP_COLOR,
                (powerup["position"][0] + offset_x, powerup["position"][1] + offset_y, CELL_SIZE, CELL_SIZE),
                border_radius=6
            )

        self.snake.draw(screen, alpha, (offset_x, offset_y))

        for p in self.particles:
            pygame.draw.circle(
                screen,
                p["color"],
                (int(p["x"] + offset_x), int(p["y"] + offset_y)),
                p["size"]
            )

        for popup in self.popups:
            text = self.small_font.render(popup["text"], True, popup["color"])
            screen.blit(
                text,
                (popup["x"] - text.get_width() / 2 + offset_x,
                 popup["y"] - text.get_height() / 2 + offset_y)
            )

        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(
            score_text,
            (WINDOW_WIDTH - score_text.get_width() - 10, 10)
        )

        if self.combo_count > 1:
            combo_text = self.font.render(f"Combo x{self.combo_count}", True, COMBO_COLOR)
            screen.blit(combo_text, (10, 10))

        if self.active_powerup and self.powerup_timer > 0:
            label = "SLOW" if self.active_powerup == "slow" else "2X SCORE"
            power_text = self.small_font.render(f"{label} {self.powerup_timer:0.1f}s", True, POWERUP_COLOR)
            screen.blit(power_text, (10, 42))

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
