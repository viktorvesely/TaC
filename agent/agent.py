from agent.agent_interface import AgentInterface
import numpy as np


class Agent(AgentInterface):
    def __init__(self, x, y, color, world):
        self.pos_x = x
        self.pos_y = y
        self.world = world
        self.color = color

    def move(self):
        """
        Moves the agent in the environment in a random direction.
        """
        # Randomly select the next action
        direction = np.random.choice(['up', 'down', 'left', 'right'])

        # Get world size
        width = self.world.size
        height = self.world.size

        if direction == 'up' and self.pos_y > 0:
            self.pos_y -= 1
        elif direction == 'down' and self.pos_y < height - 1:
            self.pos_y += 1
        elif direction == 'left' and self.pos_x > 0:
            self.pos_x -= 1
        elif direction == 'right' and self.pos_x < width - 1:
            self.pos_x += 1
