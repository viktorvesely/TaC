from typing import Callable
from pygame import Surface
import pygame
import numpy as np

from .agent_interface import AgentInterface
from .btree.btState import BTState
from .agent_actions import AgentActions

from ...state import State

state = State()

class Agent(AgentInterface):

    def __init__(self, n: int):
        super().__init__(None)
        
        state.agent_position = (np.random.random((n, 2)) -  0.5) * 300
        self.max_speed = 0.1
        self.n = n
        state.agent_velocity = np.zeros((n, 2))
        state.agent_angle = np.random.random(n) * np.pi * 2

        self.actions: list[Callable[[int], Callable]] = [AgentActions.select_action for _ in range(n)]


    def look_random(self, i_agent: int):
        state.agent_angle[i_agent] = state.agent_angle[i_agent] + (0.0008 * state.dTick) % (np.pi * 2)

    def tick(self):
        """
        Moves the agent in the environment in a random direction.
        """
        
        super().tick()

        for i, action in enumerate(self.actions):
            nex_action = action(i)
            self.actions[i] = nex_action
        # 
        state.agent_velocity = np.vstack((np.cos(state.agent_angle), np.sin(state.agent_angle))).T * self.max_speed
        

    def draw(self, surface: Surface):
        
        additive = np.ones((self.n, 3))
        additive[:, :2] = state.agent_position
    
        projected = state.camera.worldToScreen.m @ additive.T
        projected = projected[:2, :].T

        # Draw agent as circle at position
        for position in projected:
            pygame.draw.circle(surface, (255, 255, 255), position, 10 * state.camera.zoom)
