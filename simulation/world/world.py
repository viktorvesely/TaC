from pygame import Surface
import pygame

from ..entities.agents.agent import Agent
from ..window import Window

from .world_interface import WorldInterface
from .grid import Grid
from .vision_interface import Vision
from .poi import PointsOfInterests
from .navigation import GoogleMaps

import numpy as np

class World(WorldInterface):             # Concrete implementation of WorldInterface
    def __init__(self, window: Window):
        
        n_agents = 250
        self.window = window
        self.agents = Agent(n_agents)
        self.grid: Grid = Grid(n_grids=20)
        self.vision: Vision = Vision(self.grid)
        self.pois = PointsOfInterests(self.grid)
        self.pois.add_random(5)
        self.maps = GoogleMaps(self.grid, self.pois)
            
    
    def add_agent(self, agent: Agent):  # Add agents to world
        self.agents.append(agent)

    def add_pois(self, N: int = 1):
        self.pois.add_random(N)
    
    def step(self):                     # Advance agents' states in world
        for agent in self.agents:
            agent.move()
    
    def get_agents(self):               # Return list of all agents currently in world
        return self.agents
    
    def draw(self, surface: Surface):   # Draw current state of the world to given surface

        surface.fill((0, 0, 0))
        self.agents.draw(surface)
        self.grid.draw(surface)
        self.pois.draw(surface)
        self.vision.draw(surface)

        pygame.display.flip()

    def tick(self):
        # After each tick Check for collisions and update agent positions
        self.agents.tick()
        self.grid.tick()
        self.vision.tick()
        # self.maps.tick()
        
    def handle_collisions(self):
        #Cases to handle:
        # - Agent collides with wall
        # - Agent collides with another agent
            # - Thief and Citizen collides
            # - Thief and Thief collides
            # - Citizen and Citizen collides
        pass
    
    def check_collision(self, agent1: Agent, agent2: Agent):
        pass
    
    def resolve_collision(self, agent1: Agent, agent2: Agent):
        pass
                    
    def populate_world(self, n_agents: int):
        n_thiefs = int(n_agents * 0.3)                   # 30% thieves
        n_citizens = n_agents - n_thiefs

        agent_data = [
            (Thief, n_thiefs ,np.array([255, 0, 0])),    # Thieves are red
            (Citizen, n_citizens, np.array([0, 255, 0])) # Citizens are green
        ]
        
        for agent_type, n, color in agent_data:
            for _ in range(n):
                position =  self.window.window_size * np.random.rand(2) - self.window.window_size / 2   # In random position within window
                agent = agent_type(position, color)                                                     # Create agent of agent_type
                self.add_agent(agent)                                                                   # Add agent to world