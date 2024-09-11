from pygame import Surface
import pygame
from .agent_interface import AgentInterface

import numpy as np
from ...state import State

state = State()


class Agent(AgentInterface):

    def __init__(self, position: np.ndarray, color: np.ndarray):
        super().__init__(position)
        
        self.color = color
        self.max_speed = 0.1

        self._angle = np.random.random() * np.pi * 2


    def tick(self):
        """
        Moves the agent in the environment in a random direction.
        """
        super().tick()

        self._angle += (0.0001 * state.dTick) % (np.pi * 2)
        self.velocity = np.array([np.cos(self._angle), np.sin(self._angle)]) * self.max_speed
        

    def draw(self, surface: Surface):
        pygame.draw.circle(surface, self.color, state.camera.worldToScreen @ self.position, 10 * state.camera.zoom)
