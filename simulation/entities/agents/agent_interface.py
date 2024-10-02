from numpy import ndarray

from simulation.state import State
from ..entity import Entity

class AgentInterface(Entity):
    # Base class for agents in simulation, inherit Entity and add agent specific features
    def __init__(self, state: State) -> None:
        super().__init__() # Initialize agent's position
        self.state = state


    def tick(self):

        # Calculate agent's next position based on current position, velocity and tick
        self.state.agent_position = self.state.agent_position + self.state.agent_velocity * self.state.dTick
        self.state.agent_coords = self.state.world.grid.vectorized_world_to_cell(self.state.agent_position)
        
        return super().tick()


