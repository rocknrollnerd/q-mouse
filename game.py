import pygame
import numpy as np

from agents import Cheese, Cat


class Game(object):

    def __init__(self, window_size, world, agents):
        self.side = window_size[0] / world.width
        self.screen = pygame.display.set_mode(window_size)
        self.window_size = window_size
        self.set_agents(agents)
        self.world = world

    def set_agents(self, agents):
        self.agents = agents
        for a in self.agents:
            a.game = self

    def draw(self):
        self.screen.fill((255, 255, 255))
        for i in xrange(self.world.width):
            for j in xrange(self.world.height):
                c = self.world.cells[i, j]
                if c.occupied:
                    pygame.draw.rect(self.screen, (0, 0, 0), (c.x * self.side, c.y * self.side, self.side, self.side), 0)

    def draw_agent(self, agent):
        self.blank(agent.old_x, agent.old_y)
        pygame.draw.rect(self.screen, agent.colour, (agent.x * self.side, agent.y * self.side, self.side, self.side), 0)

    def get_agent_by_position(self, x, y):
        for a in self.agents:
            if a.x == x and a.y == y:
                return a

    def get_state(self, agent):
        state = []
        for dx in range(-agent.lookup_distance, agent.lookup_distance + 1):
            for dy in range(-agent.lookup_distance, agent.lookup_distance + 1):
                if dx == 0 and dy == 0:
                    continue
                other_agent = self.get_agent_by_position(agent.x + dx, agent.y + dy)
                if not self.world.is_free(agent.x + dx, agent.y + dy):
                    # wall / world border
                    value = 0
                elif not other_agent:
                    # free cell
                    value = 1
                else:
                    # other agent's value (may be different)
                    value = other_agent.value
                state.append(value)
        return tuple(state)

    # def get_state(self, agent):
    #     state = []
    #     for dx in range(-agent.lookup_distance, agent.lookup_distance + 1):
    #         row = []
    #         for dy in range(-agent.lookup_distance, agent.lookup_distance + 1):
    #             if not self.world.is_free(agent.x + dx, agent.y + dy):
    #                 value = 0
    #             else:
    #                 value = 1
    #                 other_agent = self.get_agent_by_position(agent.x + dx, agent.y + dy)
    #                 if other_agent:
    #                     value = other_agent.value
    #             row.append(value)
    #         state.append(row)
    #     return np.array(state)

    def get_reward(self, agent):
        for other_agent in self.agents:
            if agent == other_agent:
                continue
            if other_agent.x == agent.x and other_agent.y == agent.y:
                return other_agent.reward
        return -1

    def blank(self, x, y):
        pygame.draw.rect(self.screen, (255, 255, 255), (x * self.side, y * self.side, self.side, self.side), 0)

    def update(self):
        for a in self.agents:
            a.update()
            self.draw_agent(a)
