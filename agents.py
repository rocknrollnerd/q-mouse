import random
import numpy as np


class Agent(object):

    def __init__(self, world, colour, position=None, lookup_distance=2, value=2, reward=None):
        from ai import Qlearning, QlearningSmartExploration, QLearningApproxLinear

        self.world = world
        if not position:
            self.set_random_position()
        else:
            self.x, self.y = position
        self.old_x, self.old_y = self.x, self.y
        self.colour = colour
        self.lookup_distance = lookup_distance  # how far an agent can see
        self.value = value
        self.reward = reward  # if the agent is valuable; say, cheesy cheese
        self.ai = QlearningSmartExploration()
        self.ai.agent = self
        self.last_state = None
        self.last_action = None
        self.win = False
        self.failed = False
        self.learning_turns = 0

    def set_random_position(self):
        c = random.choice(self.world.free_cells)
        self.x, self.y = c.x, c.y

    def get_actions(self):
        actions = []
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, +1)):
            if self.world.is_free(self.x + dx, self.y + dy) or (dx == 0 and dy == 0):
                actions.append((dx, dy))
        return actions

    def make_action(self, state, action):
        self.old_x, self.old_y = self.x, self.y  # to clear agent's trail
        self.last_state = state
        self.last_action = action
        dx, dy = action
        self.x += dx
        self.y += dy


class Cheese(Agent):

    def update(self):
        pass


class Mouse(Agent):

    def get_cheese(self):
        return [a for a in self.game.agents if isinstance(a, Cheese)][0]

    def get_cat(self):
        # return None
        cats = [a for a in self.game.agents if isinstance(a, Cat)]
        if cats:
            return cats[0]

    def update(self):
        state = self.game.get_state(self)
        reward = self.game.get_reward(self)
        actions = self.get_actions()
        cheese = self.get_cheese()
        cat = self.get_cat()
        state = (state, cheese, cat)
        if self.last_state is not None and self.last_action is not None:
            self.ai.learn(self.last_state, self.last_action, reward, state, actions)
            self.learning_turns += 1

        # now if reward, reset position
        if reward > 0:
            print 'cheese obtained!'
            # raw_input()
            self.win = True
        elif reward < -1:
            print 'mouse is eaten ('
            self.failed = True
        else:
            # else, goto sweet cheese
            action = self.ai.choose_action(state, actions)
            # print 'chose', action
            # raw_input()
            self.make_action(state, action)


class Cat(Agent):

    """
    Cat is kinda stupid. When it cannot see the mouse,
    it moves randomly, other way it goes directly to the mouse.
    It also sometimes does a random action even when sees the mouse,
    to get the mouse a chance to escape.
    """

    def euclidean(self, x0, y0, x1, y1):
        return np.sqrt((x0 - x1) ** 2 + (y0 - y1) ** 2)

    def get_mouse(self):
        mouse = [a for a in self.game.agents if isinstance(a, Mouse)]
        if mouse:
            return mouse[0]

    def sees_mouse(self, mouse):
        if not mouse:
            return False, None
        dist_to_mouse = self.euclidean(self.x, self.y, mouse.x, mouse.y)
        if dist_to_mouse > self.lookup_distance:
            return False, None
        else:
            return True, (mouse.x, mouse.y)

    def goto_mouse(self, mouse_x, mouse_y, actions):
        # choose the action that'll get you closer to the mouse
        # if there are multiple such actions, choose randomly
        metrics = []
        for dx, dy in actions:
            metrics.append(self.euclidean(mouse_x, mouse_y, self.x + dx, self.y + dy))
        max_actions = [a for i, a in enumerate(actions) if metrics[i] == min(metrics)]
        return random.choice(max_actions)

    def update(self):
        mouse = self.get_mouse()
        state = self.game.get_state(self)
        actions = self.get_actions()
        sees_mouse, mouse_location = self.sees_mouse(mouse)
        if random.random() < 0.1 or not sees_mouse:
            action = random.choice(actions)
        else:
            action = self.goto_mouse(*mouse_location, actions=actions)
        self.make_action(state, action)
