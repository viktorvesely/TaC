from pygame import Surface
import pygame

from ..entities.agent import Agent
from ..window import Window

from .world_interface import WorldInterface


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