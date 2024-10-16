from typing import Callable
from matplotlib import pyplot as plt
from pygame import Surface
import pygame
import numpy as np
import random

from .agent_interface import AgentInterface
from .agent_actions import ActionFunc
from .thief_actions import ThiefActions
from .citizen_actions import CitizenActions

from ...state import State
from ...utils import Utils
from ...events.event import MovementEvent
import matplotlib as mpl



class Agent(AgentInterface):

    def __init__(self, state: State, n_thieves: int, n_citizens: int):
        super().__init__(state)

        n = n_thieves + n_citizens
        
        self.state.agent_position = np.zeros((n, 2))

        self.n = n
        self.pos_save_period = 1000
        self.next_t_pos_save = self.state.t + self.pos_save_period

        self.state.agent_velocity = np.zeros((n, 2))
        self.state.agent_angle = np.random.random(n) * np.pi * 2
        self.state.n_agents = n
        self.state.agent_colors = np.zeros((n, 3), dtype=np.int32)
        self.state.agent_colors[:, :] = 255 # White color initialization
        self.state.agent_speed = np.full((n, 1), 0.1)
        self.state.agent_motivations = np.zeros((n,1)) # Array of motivations for each agent
        self.state.agent_is_citizen = np.full(n, True)
        self.state.agent_is_citizen[n_citizens:] = False
        self.state.agent_heading_vec = np.vstack((np.cos(self.state.agent_angle), np.sin(self.state.agent_angle))).T
        self.state.agent_last_rob = np.full(n, self.state.t)
        self.actions: list[ActionFunc] = []


        for i in range(n):
            if self.state.agent_is_citizen[i]:
                #setting the citizen color to green
                self.state.agent_colors[i, 0] = 0
                self.state.agent_colors[i, 1] = 255
                self.state.agent_colors[i, 2] = 0
                self.actions.append(CitizenActions.select_action)
            else:
                #setting the thief color to red
                self.state.agent_colors[i, 0] = 255
                self.state.agent_colors[i, 1] = 0
                self.state.agent_colors[i, 2] = 0
                # setting the thief motivation to 0.5
                self.state.agent_motivations[i,0] = 0
                self.actions.append(ThiefActions.select_almost_empty_area)
        #self.close_range = 0.1

    def look_random(self, i_agent: int, multiplier: float):
        self.state.agent_angle[i_agent] = self.state.agent_angle[i_agent] + (0.0008 * multiplier * self.state.dTick) % (np.pi * 2)

    def tick(self):
        """
        Moves the agent in the environment in a random direction.
        """
        
        super().tick()

        thief_mask = ~self.state.agent_is_citizen
        factor = 0.0001
        bias = 2 # Above 2 means more toward gaining motivation bellow to towards loosing NOT LINEAR!!!

        max_md = factor - (factor / bias)
        min_md = -(factor / bias)
        need_boost = 1
        max_need = abs(min_md) * need_boost
        time_max_boost = 5_000

        k = 0.11
        l = 1.1

        thiefs_coords = self.state.agent_coords[thief_mask, :]
        thiefs_vision_values = self.state.world.vision.values[tuple(thiefs_coords.T)]
        
        delta_last_rob = self.state.t - self.state.agent_last_rob[thief_mask]     
        t = np.clip(delta_last_rob, 0, time_max_boost) / time_max_boost
        from_vision = (factor *(1 - thiefs_vision_values) - (factor / bias))
        from_last_rob = ((-k) / (t -l) - (k/l)) * max_need
        delta_motivation = (
            self.state.vars.vision_weight * from_vision +
            self.state.vars.frustration_weight * from_last_rob
        ) * self.state.dTick
        
        self.state.agent_motivations[~self.state.agent_is_citizen, :] += delta_motivation[:, np.newaxis]
        self.state.agent_motivations = np.clip(self.state.agent_motivations, 0.0, 1.0) 

        for i_agent, action in enumerate(self.actions):
            next_action = action(i_agent, self.state)
            self.actions[i_agent] = next_action

            if i_agent == self.state.debug_i_agent_print_action:
                print(
                    "citizen" if self.state.agent_is_citizen[i_agent] else "thief",
                    i_agent,
                    action.__name__
                )
        # 
        self.state.agent_heading_vec = np.vstack((np.cos(self.state.agent_angle), np.sin(self.state.agent_angle))).T
        self.state.agent_velocity = self.state.agent_heading_vec * self.state.agent_speed

        if self.state.t >= self.next_t_pos_save:
            self.next_t_pos_save = self.state.t + self.pos_save_period
            # MovementEvent(self.state.agent_position.astype(np.float32))            

    

    def draw(self, surface: Surface):
        
        forward_vec =  self.state.agent_position + self.state.agent_heading_vec * 12
        projected = Utils.vectorized_projection(self.state.camera.worldToScreen.m, self.state.agent_position)
        forward_vec = Utils.vectorized_projection(self.state.camera.worldToScreen.m, forward_vec)

        t_colors = self.state.agent_motivations[~self.state.agent_is_citizen]
        t_colors = np.squeeze(t_colors)
        t_colors = np.pad(t_colors, 1)
        t_colors[-1] = 1
        t_colors = mpl.colormaps["plasma"](t_colors) * 255
        t_colors = t_colors[1:-1, :]
        t_colors = t_colors[:, :3].astype(np.int32)
        self.state.agent_colors[~self.state.agent_is_citizen, :] = t_colors


        # Draw agent as circle at position
        for i_agent, position in enumerate(projected):
            pygame.draw.circle(surface, self.state.agent_colors[i_agent, :], position, self.state.vars.agent_size * self.state.camera.zoom)
            pygame.draw.line(surface, (255, 255, 255), position, forward_vec[i_agent], width=int(3 * self.state.camera.zoom))
