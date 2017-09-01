import pygame
import random

from world import DrawnWorld, RandomWorld
from agents import Mouse, Cheese, Cat
from game import Game


if __name__ == '__main__':

    pygame.init()
    world = DrawnWorld('worlds/barriers.txt')
    # world = RandomWorld(20, 20)
    mouse = Mouse(world, (125, 125, 125), lookup_distance=5, position=random.choice(world.mouse_locations))
    cheese = Cheese(world, (217, 243, 50), position=random.choice(world.cheese_locations), value=2, reward=50)
    cat = Cat(world, (255, 0, 0), lookup_distance=5, position=random.choice(world.cat_locations), value=3, reward=-100)
    game = Game((600, 600), world, [cat, mouse, cheese])
    game.draw()
    clock = pygame.time.Clock()

    turns = 0
    learning_turns = 5000

    while True:
        game.update()
        if mouse.win or mouse.failed:
            turns += 1
            print turns
            game.blank(mouse.x, mouse.y)
            mouse.x, mouse.y = random.choice(world.mouse_locations)
            # mouse.set_random_position()
            mouse.last_action = mouse.last_state = None
            mouse.win = mouse.failed = False

            # also restart cat
            game.blank(cat.x, cat.y)
            cat.x, cat.y = random.choice(world.cat_locations)

        if turns > learning_turns:
            pygame.display.update()
            # slowdown game speed
            clock.tick(10)
    pygame.quit()
