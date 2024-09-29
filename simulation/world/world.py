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

state = State() 

class World(WorldInterface):             # Concrete implementation of WorldInterface
    def __init__(self, window: Window):
        
        self.generator = WorldGenerator(state.vars.n_grids)
        self.window = window
        self.agents = Agent(state.vars.n_thieves, state.vars.n_citizens)
        self.grid: Grid = Grid(self.generator.generate_walls())
        self.vision: Vision = Vision(self.grid)
        self.pois: PointsOfInterests = PointsOfInterests(self.grid)
        self.pois.add_random(5)
        self.maps = GoogleMaps(self.grid, self.pois)
        
        state.maps = self.maps
        state.grid = self.grid
            
    
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

        self.window.manager.draw_ui(surface)

        pygame.display.flip()

    def tick(self):
        # After each tick Check for collisions and update agent positions
        self.agents.tick()
        self.grid.tick()
        self.vision.tick()
        # self.maps.tick()
   