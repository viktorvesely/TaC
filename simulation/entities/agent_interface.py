import numpy as np
from numpy import ndarray

from ..state import State
from .entity import Entity

state = State()

class AgentInterface(Entity):
    
    def __init__(self, positon: ndarray) -> None:
        super().__init__(positon)

        self.velocity: np.ndarray = np.zeros(2)


    def tick(self):

        next_pos = self.position + self.velocity * state.dTick
        self.position = next_pos

        return super().tick()