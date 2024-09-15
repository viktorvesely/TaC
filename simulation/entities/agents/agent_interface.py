import numpy as np
from numpy import ndarray

from simulation.state import State
from ..entity import Entity

state = State()

class AgentInterface(Entity):
    
    def __init__(self, positon: ndarray) -> None:
        super().__init__(positon)

   


    def tick(self):

        self.position = self.position + self.velocity * state.dTick
        
        return super().tick()