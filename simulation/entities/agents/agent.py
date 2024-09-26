from typing import Callable
from pygame import Surface
import pygame
import numpy as np
import random

from .agent_interface import AgentInterface
from .agent_actions import AgentActions
from .thief_actions import ThiefActions

from ...state import State

state = State()

class Agent(AgentInterface):

    def __init__(self, n: int):
        super().__init__(None)
        
        state.agent_position = (np.random.random((n, 2)) -  0.5) * 300
        self.n = n
        state.agent_velocity = np.zeros((n, 2))
        state.agent_angle = np.random.random(n) * np.pi * 2
        state.n_agents = n
        state.agent_colors = np.zeros((n, 3), dtype=np.int32)
        state.agent_colors[:, :] = 255
        state.agent_speed = np.full((n, 1), 0.1)
        state.agent_role = np.random.choice([True,False],n,p=[0.7,0.3]) #Array of booleans where True represents citizen and False represents thief
        self.actions: list[Callable[[int], Callable]] = []
        for i in range(n):
            if state.agent_role[i]:
                #setting the citizen color to green
                state.agent_colors[i, 0] = 0
                state.agent_colors[i, 1] = 255
                state.agent_colors[i, 2] = 0
                self.actions.append(AgentActions.roaming())
            else:
                #setting the thief color to red
                state.agent_colors[i, 0] = 0
                state.agent_colors[i, 1] = 0
                state.agent_colors[i, 2] = 255
                self.actions.append(ThiefActions.start_looking_for_target(i))
        #self.close_range = 0.1

    def look_random(self, i_agent: int, multiplier: float):
        state.agent_angle[i_agent] = state.agent_angle[i_agent] + (0.0008 * multiplier * state.dTick) % (np.pi * 2)

    def tick(self):
        """
        Moves the agent in the environment in a random direction.
        """
        
        super().tick()
        for i, action in enumerate(self.actions):
            nex_action = action(i)
            self.actions[i] = nex_action
        # 
        state.agent_velocity = np.vstack((np.cos(state.agent_angle), np.sin(state.agent_angle))).T * state.agent_speed
        

    def draw(self, surface: Surface):
        
        additive = np.ones((self.n, 3))
        additive[:, :2] = state.agent_position
    
        projected = state.camera.worldToScreen.m @ additive.T
        projected = projected[:2, :].T

        # Draw agent as circle at position
        for i_agent, position in enumerate(projected):
            pygame.draw.circle(surface, state.agent_colors[i_agent, :], position, 10 * state.camera.zoom)
