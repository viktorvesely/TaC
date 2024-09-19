from .agent import Agent
import numpy as np

class Thief(Agent):
    def __init__(self, position: np.ndarray, color: np.ndarray):
        super().__init__(position, color)
        self.role = "thief"
        self.color = np.array([255, 0, 0])
        
    def behaviour(self):
        # Thief specific behavior
        print("I am a thief")





""" Possible implementation of thief's movement towards target
class Thief(AgentInterface):
    def __init__(self, position: ndarray, target: ndarray) -> None:
        super().__init__(position)
        self.target = target
        self.role = "thief"

    def tick(self):
        direction = self.target - self.position
        self.velocity = direction / np.linalg.norm(direction) * 10  # Move towards the target.
        super().tick()
"""