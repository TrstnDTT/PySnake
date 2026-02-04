import pygame
from settings import SNAKE_COLOR, CELL_SIZE

class Snake:
    def __init__(self, x, y):
        self.segments = [(x, y)]
        self.prev_segments = [(x, y)]
        self.dx = CELL_SIZE
        self.dy = 0
        self.size = CELL_SIZE
        self.pending_growth = 0

    @property
    def x(self):
        return self.segments[0][0]

    @property
    def y(self):
        return self.segments[0][1]
    
    def move(self):
        self.prev_segments = self.segments.copy()
        new_head = (self.x + self.dx, self.y + self.dy)
        self.segments.insert(0, new_head)
        if self.pending_growth > 0:
            self.pending_growth -= 1
        else:
            self.segments.pop()

        if len(self.prev_segments) < len(self.segments):
            self.prev_segments = [self.prev_segments[0]] + self.prev_segments
        if len(self.prev_segments) > len(self.segments):
            self.prev_segments = self.prev_segments[:len(self.segments)]
    
    def change_direction(self, direction):
        if len(self.segments) > 1:
            if direction == "UP" and self.dy == CELL_SIZE:
                return
            if direction == "DOWN" and self.dy == -CELL_SIZE:
                return
            if direction == "LEFT" and self.dx == CELL_SIZE:
                return
            if direction == "RIGHT" and self.dx == -CELL_SIZE:
                return
        if direction == "UP":
            self.dx, self.dy = 0, -CELL_SIZE
        if direction == "DOWN":
            self.dx, self.dy = 0, CELL_SIZE
        if direction == "LEFT":
            self.dx, self.dy = -CELL_SIZE, 0
        if direction == "RIGHT":
            self.dx, self.dy = CELL_SIZE, 0

    def grow(self, amount=1):
        self.pending_growth += amount

    def is_self_collision(self):
        return (self.x, self.y) in self.segments[1:]
    
    def draw(self, screen, alpha=1.0, offset=(0, 0)):
        for index, segment in enumerate(self.segments):
            prev = self.prev_segments[index] if index < len(self.prev_segments) else segment
            render_x = prev[0] + (segment[0] - prev[0]) * alpha
            render_y = prev[1] + (segment[1] - prev[1]) * alpha
            color = SNAKE_COLOR if index == 0 else (max(0, SNAKE_COLOR[0] - 30),
                                                    max(0, SNAKE_COLOR[1] - 30),
                                                    max(0, SNAKE_COLOR[2] - 30))
            pygame.draw.rect(
                screen,
                color,
                (render_x + offset[0], render_y + offset[1], CELL_SIZE, CELL_SIZE)
            )
