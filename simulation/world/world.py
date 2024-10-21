from pygame import Surface
import pygame
import numpy as np

from ..entities.agents.agent import Agent
from ..window import Window
from ..state import State

from .world_interface import WorldInterface
from .grid import Grid
from .vision_interface import Vision
from .poi import PointsOfInterests
from .navigation import GoogleMaps
from .generation import WorldGenerator
from ..events.event import MapEvent


class World(WorldInterface):             # Concrete implementation of WorldInterface
    def __init__(self, state: State, window: Window):
        
        self.generator = WorldGenerator(state, state.vars.n_grids)
        self.window = window
        self.agents = Agent(state, state.vars.n_thieves, state.vars.n_citizens)

        walls = self.generator.generate_walls()
        MapEvent(state, walls)
        self.grid: Grid = Grid(state, walls)
        self.vision: Vision = Vision(state, self.grid)
        self.pois: PointsOfInterests = PointsOfInterests(state, self.grid)
        self.pois.register_existing()
        self.maps = GoogleMaps(state, self.grid, self.pois)

        state.maps = self.maps
        state.grid = self.grid
        state.agent_coords, state.agent_position = self.grid.generate_agent_positions()
            
    
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
   