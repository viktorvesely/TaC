from pygame import Surface
import pygame

from ..entities.agent import Agent
from ..entities.citizen import Citizen  
from ..entities.thief import Thief
from ..window import Window

from .world_interface import WorldInterface

import numpy as np


class World(WorldInterface):
    def __init__(self, window: Window):
        self.agents: list[Agent] = []
        self.window = window
        
    
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

        pygame.display.flip()

    def tick(self):

        for agent in self.agents:
            agent.tick()
            
    def populate_world(self, n_agents: int):
        n_thiefs = int(n_agents * 0.3)
        n_citizens = n_agents - n_thiefs

        agent_data = [
            (Thief, n_thiefs ,np.array([255, 0, 0])),
            (Citizen, n_citizens, np.array([0, 255, 0]))
        ]
        
        for agent_type, n, color in agent_data:
            for _ in range(n):
                position =  self.window.window_size * np.random.rand(2)
                agent = agent_type(position, color)
                self.add_agent(agent)