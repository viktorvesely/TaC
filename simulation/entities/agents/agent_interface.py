import numpy as np
from numpy import ndarray

from simulation.state import State
from ..entity import Entity

state = State()

class AgentInterface(Entity):
    
    def __init__(self, positon: ndarray) -> None:
        super().__init__(positon)


    def tick(self):

        state.agent_position = state.agent_position + state.agent_velocity * state.dTick
        state.agent_coords = state.world.grid.vectorized_world_to_cell(state.agent_position)
        
        return super().tick()