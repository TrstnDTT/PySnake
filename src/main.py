import pygame
from settings import WINDOW_HEIGHT, WINDOW_WIDTH, FPS
from game import Game

pygame.init()
pygame.display.set_caption("PySnake")

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
clock = pygame.time.Clock()
running = True
game = Game()

while (running):
    dt = clock.tick(FPS) / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        else: 
            game.handle_event(event)
    game.update(dt)
    game.draw(screen)
    pygame.display.flip()

pygame.quit()
