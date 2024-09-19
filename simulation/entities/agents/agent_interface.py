import numpy as np
from numpy import ndarray

from simulation.state import State
from ..entity import Entity

state = State()

class AgentInterface(Entity):
    # Base class for agents in simulation, inherit Entity and add agent specific features
    def __init__(self, positon: ndarray) -> None:
        super().__init__(positon) # Initialize agent's position


    def tick(self):

        # Calculate agent's next position based on current position, velocity and tick
        state.agent_position = state.agent_position + state.agent_velocity * state.dTick
        state.agent_coords = state.world.grid.vectorized_world_to_cell(state.agent_position)
        
        return super().tick()


