import pygame
import random
from settings import CELL_SIZE, WINDOW_WIDTH, WINDOW_HEIGHT, FOOD_COLOR

class Food:
    def __init__(self):
        self.position = (0, 0)

    def respawn(self, snake_positions):
        max_cols = WINDOW_WIDTH // CELL_SIZE
        max_rows = WINDOW_HEIGHT // CELL_SIZE

        while True:
            x = random.randint(0, max_cols -1) * CELL_SIZE
            y = random.randint(0, max_rows -1) * CELL_SIZE
            if (x,y) not in snake_positions:
                self.position = (x, y)
                break

    def draw(self, screen, offset=(0, 0)):
        pygame.draw.rect(
            screen,
            FOOD_COLOR,
            (self.position[0] + offset[0], self.position[1] + offset[1], CELL_SIZE, CELL_SIZE)
        )
