from pygame import Surface
import pygame

from ..entities.agents.agent import Agent
from ..entities.agents.citizen import Citizen  
from ..entities.agents.thief import Thief
from ..window import Window

from .world_interface import WorldInterface
from .grid import Grid

import numpy as np


class World(WorldInterface):
    def __init__(self, window: Window):
        self.agents: list[Agent] = []
        self.window = window

        self.grid: Grid = Grid()
        
    
    def add_agent(self, agent: Agent):
        self.agents.append(agent)
    
    def step(self):
        for agent in self.agents:
            agent.move()
    
    def get_agents(self):
        return self.agents
    
    def draw(self, surface: Surface):

        self.window.pygame_event_handler()

        surface.fill((0, 0, 0))

        for agent in self.agents:
            agent.draw(surface)

        self.grid.draw(surface)

        pygame.display.flip()

    def tick(self):
        # After each tick Check for collisions and update agent positions
        for agent in self.agents:
            agent.tick()
        
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
    
    def handle_thief_citizen_collision(self, thief: Thief, citizen: Citizen):
        # Call behavior when a thief collides with a citizen
        pass

    def handle_thief_thief_collision(self, thief1: Thief, thief2: Thief):
        # Call specific behavior when thieves collide
        pass

    def handle_citizen_citizen_collision(self, citizen1: Citizen, citizen2: Citizen):
        # Call specific behavior when citizens collide
        pass
                    
    def populate_world(self, n_agents: int):
        n_thiefs = int(n_agents * 0.3)
        n_citizens = n_agents - n_thiefs

        agent_data = [
            (Thief, n_thiefs ,np.array([255, 0, 0])),
            (Citizen, n_citizens, np.array([0, 255, 0]))
        ]
        
        for agent_type, n, color in agent_data:
            for _ in range(n):
                position =  self.window.window_size * np.random.rand(2) - self.window.window_size / 2
                agent = agent_type(position, color)
                self.add_agent(agent)