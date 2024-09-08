from .agent import Agent
import numpy as np

class Thief(Agent):
    def __init__(self, position: np.ndarray, color: np.ndarray):
        super().__init__(position, color)
        self.role = "thief"
        self.color = np.array([255, 0, 0])
        
    def behaviour(self):
        print("I am a thief")
