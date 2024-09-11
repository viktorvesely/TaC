import numpy as np
from numpy import ndarray

from simulation.state import State
from ..entity import Entity

state = State()

class AgentInterface(Entity):
    
    def __init__(self, positon: ndarray) -> None:
        super().__init__(positon)

        self.velocity: np.ndarray = np.zeros(2)


    def tick(self):

        state.agent_positions = state.agent_positions + self.velocity * state.dTick

        return super().tick()