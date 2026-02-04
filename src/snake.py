import pygame
from settings import SNAKE_COLOR, CELL_SIZE

class Snake:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.prev_x = x
        self.prev_y = y
        self.dx = CELL_SIZE
        self.dy = 0
        self.size = CELL_SIZE
    
    def move(self):
        self.prev_x = self.x
        self.prev_y = self.y
        self.x += self.dx
        self.y += self.dy
    
    def change_direction(self, direction):
        if direction == "UP":
            self.dx, self.dy = 0, -CELL_SIZE
        if direction == "DOWN":
            self.dx, self.dy = 0, CELL_SIZE
        if direction == "LEFT":
            self.dx, self.dy = -CELL_SIZE, 0
        if direction == "RIGHT":
            self.dx, self.dy = CELL_SIZE, 0
    
    def draw(self, screen, alpha=1.0):
        render_x = self.prev_x + (self.x - self.prev_x) * alpha
        render_y = self.prev_y + (self.y - self.prev_y) * alpha
        pygame.draw.rect(
            screen,
            SNAKE_COLOR,
            (render_x, render_y, CELL_SIZE, CELL_SIZE)
        )
