import pygame
from settings import WINDOW_HEIGHT, WINDOW_WIDTH, FOOD_COLOR, FPS, BG_COLOR
from game import Game

pygame.init()

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
            Game.handle_event(game, event)
    Game.update(game, dt)
    screen.fill(BG_COLOR)
    Game.draw(game, screen)
    pygame.display.flip()

pygame.quit()
