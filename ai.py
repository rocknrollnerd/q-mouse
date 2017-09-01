import random
import numpy as np

from agents import Cat, Cheese, Mouse


class Qlearning(object):

    def __init__(self, epsilon=0.1, alpha=0.2, gamma=0.9):
        self.q = {}
        self.epsilon = epsilon
        self.alpha = alpha
        self.gamma = gamma

    def get_q(self, state, action):
        # None-tolerant shortcut
        return self.q.get((state, action), 0.0)

    def learn(self, prev_state, prev_action, reward, new_state, new_actions):
        new_state_max_q = max([self.get_q(new_state, a) for a in new_actions])
        old_q = self.q.get((prev_state, prev_action), None)
        if old_q is None:
            self.q[(prev_state, prev_action)] = reward
        else:
            self.q[(prev_state, prev_action)] = old_q + self.alpha * (reward + self.gamma * new_state_max_q - old_q)

    def choose_action(self, state, actions):
        if random.random() < self.epsilon:
            # time to get crazy and explore!
            return random.choice(actions)
        q_values = [self.get_q(state, a) for a in actions]
        max_q = max(q_values)

        # if multiple max values, randomize
        if q_values.count(max_q) > 1:
            best_actions = [i for i in range(len(actions)) if q_values[i] == max_q]
            return actions[random.choice(best_actions)]
        else:
            return actions[q_values.index(max_q)]


class QlearningSmartExploration(Qlearning):

    def choose_action(self, state, actions):
        q_values = [self.get_q(state, a) for a in actions]
        max_q = max(q_values)
        min_q = min(q_values)

        if random.random() < self.epsilon:
            mag = max(abs(min_q), abs(max_q))
            # add random values to all the actions, recalculate maxQ
            q_values = [q_values[i] + random.random() * mag - .5 * mag for i in range(len(actions))]
            max_q = max(q_values)

        # if multiple max values, randomize
        if q_values.count(max_q) > 1:
            best_actions = [i for i in range(len(actions)) if q_values[i] == max_q]
            return actions[random.choice(best_actions)]
        else:
            return actions[q_values.index(max_q)]


class QLearningApproxLinear(Qlearning):

    def __init__(self, epsilon=0.1, grad_descent_rate=0.01, discount=0.1):
        self.num_features = 1
        self.w = np.random.uniform(low=-0.5, high=0.5, size=(self.num_features,))
        self.epsilon = epsilon
        self.grad_descent_rate = grad_descent_rate
        self.discount = discount  # a.k.a. previous gamma

    def get_q(self, state, action):
        # None-tolerant shortcut
        f = self.feature_wrap(state, action)
        return np.dot(f, self.w)

    def choose_action(self, state, actions):
        if random.random() < self.epsilon:
            # time to get crazy and explore!
            return random.choice(actions)
        q_values = [self.get_q(state, a) for a in actions]
        max_q = max(q_values)

        # if multiple max values, randomize
        if q_values.count(max_q) > 1:
            best_actions = [i for i in range(len(actions)) if q_values[i] == max_q]
            return actions[random.choice(best_actions)]
        else:
            return actions[q_values.index(max_q)]

    def learn(self, prev_state, prev_action, reward, new_state, new_actions):
        new_state_max_q = max([self.get_q(new_state, a) for a in new_actions])
        old_q = self.get_q(prev_state, prev_action)
        delta = reward + self.discount * new_state_max_q - old_q
        self.w += self.grad_descent_rate * delta * self.feature_wrap(prev_state, prev_action)
        print self.w

    def euclidean(self, x0, y0, x1, y1):
        return np.sqrt((x0 - x1) ** 2 + (y0 - y1) ** 2)

    def feature_wrap(self, state, action):
        # makes a feature vector from state and action
        # here we just use hand-engineered features
        state, cheese, cat = state
        dx, dy = action
        f = [0]
        # now, are we moving towards the cheese?
        dist = self.euclidean(self.agent.x, self.agent.y, cheese.x, cheese.y)
        dist_after_action = self.euclidean(self.agent.x + dx, self.agent.y + dy, cheese.x, cheese.y)
        if dist_after_action < dist:
            f[0] = 1
        else:
            f[0] = -1
        return np.array(f).T
