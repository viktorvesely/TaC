from pygame import Surface
import pygame
from .agent_interface import AgentInterface
from .btree.btState import BTState
import numpy as np
from ...state import State

state = State()
btState = BTState()


class Agent(AgentInterface):

    def __init__(self, n: int):
        super().__init__(None)
        
        self.position = (np.random.random((n, 2)) -  0.5) * 400
        self.max_speed = 0.1
        self.n = n
        self.velocity = np.zeros((n, 2))

        self._angle = np.random.random(n) * np.pi * 2


    def tick(self):
        """
        Moves the agent in the environment in a random direction.
        """
        
        super().tick()

        self._angle = self._angle + (0.0001 * state.dTick) % (np.pi * 2)
        self.velocity = np.vstack((np.cos(self._angle), np.sin(self._angle))).T * self.max_speed
        

    def draw(self, surface: Surface):
       """
         Draws the agent on the screen. Must be implemented by subclasses.
       """
       ...