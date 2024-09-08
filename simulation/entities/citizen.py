from .agent import Agent

import numpy as np

class Citizen(Agent):
    def __init__(self, position: np.ndarray, color: np.ndarray):
        super().__init__(position, color)
        self.role = "citizen"
        self.color = color
        
    def behaviour(self):
        print("I am a citizen")
        
    