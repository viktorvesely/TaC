from typing import Callable
from pygame import Surface
import pygame
import numpy as np
import random

from .agent_interface import AgentInterface
from .agent_actions import AgentActions
from .thief_actions import ThiefActions
from .citizen_actions import CitizenActions

from ...utils import Utils
from ...events.event import MovementEvent
from ...state import State

state = State()

class Agent(AgentInterface):

    def __init__(self, n_thieves: int, n_citizens: int):
        super().__init__(None)

        n = n_thieves + n_citizens
        
        state.agent_position = np.zeros((n, 2))

        self.n = n
        self.pos_save_period = 1000
        self.next_t_pos_save = state.t + self.pos_save_period

        state.agent_velocity = np.zeros((n, 2))
        state.agent_angle = np.random.random(n) * np.pi * 2
        state.n_agents = n
        state.agent_colors = np.zeros((n, 3), dtype=np.int32)
        state.agent_colors[:, :] = 255 # White color initialization
        state.agent_speed = np.full((n, 1), 0.1)
        state.agent_motivations = np.zeros((n,1)) # Array of motivations for each agent
        state.agent_is_citizen = np.full(n, True)
        state.agent_is_citizen[n_citizens:] = False
        state.agent_heading_vec = np.vstack((np.cos(state.agent_angle), np.sin(state.agent_angle))).T
        self.actions: list[Callable[[int], Callable]] = []

        for i in range(n):
            if state.agent_is_citizen[i]:
                #setting the citizen color to green
                state.agent_colors[i, 0] = 0
                state.agent_colors[i, 1] = 255
                state.agent_colors[i, 2] = 0
                self.actions.append(CitizenActions.select_action(i))
            else:
                #setting the thief color to red
                state.agent_colors[i, 0] = 255
                state.agent_colors[i, 1] = 0
                state.agent_colors[i, 2] = 0
                # setting the thief motivation to 0.5
                state.agent_motivations[i,0] = 0.5
                self.actions.append(ThiefActions.selects_dense_area)
        #self.close_range = 0.1

    def look_random(self, i_agent: int, multiplier: float):
        state.agent_angle[i_agent] = state.agent_angle[i_agent] + (0.0008 * multiplier * state.dTick) % (np.pi * 2)

    def tick(self):
        """
        Moves the agent in the environment in a random direction.
        """
        
        super().tick()

        for i, action in enumerate(self.actions):
            next_action = action(i)
            self.actions[i] = next_action
        # 
        state.agent_heading_vec = np.vstack((np.cos(state.agent_angle), np.sin(state.agent_angle))).T
        state.agent_velocity = state.agent_heading_vec * state.agent_speed

        if state.t >= self.next_t_pos_save:
            self.next_t_pos_save = state.t + self.pos_save_period
            MovementEvent(state.agent_position.astype(np.float32))            

    

    def draw(self, surface: Surface):
        
        forward_vec =  state.agent_position + state.agent_heading_vec * 12
        projected = Utils.vectorized_projection(state.camera.worldToScreen.m, state.agent_position)
        forward_vec = Utils.vectorized_projection(state.camera.worldToScreen.m, forward_vec)

        # Draw agent as circle at position
        for i_agent, position in enumerate(projected):
            pygame.draw.circle(surface, state.agent_colors[i_agent, :], position, state.vars.agent_size * state.camera.zoom)
            pygame.draw.line(surface, (255, 255, 255), position, forward_vec[i_agent], width=int(3 * state.camera.zoom))
