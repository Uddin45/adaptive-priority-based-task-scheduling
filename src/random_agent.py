import numpy as np

class RandomAgent:
    def __init__(self, action_size=0):
        self.action_size = action_size

    def action(self):
        action = np.random.choice(self.action_size, 1)[0]
        return action


if __name__ == '__main__':
    r = RandomAgent(action_size=20)
    for i in range(10000):
        if r.action() == 0:
            print(r.action())
