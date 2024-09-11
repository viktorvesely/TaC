import arcade
from .agent_interface import AgentInterface

import numpy as np
from ...state import State
from ...utils import Utils

state = State()


class Agent(AgentInterface):

    def __init__(self, n: int):
        super().__init__(None)
        
        state.agent_positions = (np.random.random((n, 2)) -  0.5) * 400
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
        

    def draw(self):
        
        n_agents = state.agent_positions.shape[0]
        draw_agents = state.agent_positions.copy()
        offset = np.array([10, 10]) * state.camera.zoom

        points = Utils.create_proojected_rect_mesh_array(draw_agents, offset, state.camera.worldToScreen.m)

        colors = np.repeat(np.array(arcade.color.RED)[np.newaxis, :], n_agents * 4, axis=0)

        shape_list = arcade.ShapeElementList()
        shape = arcade.create_rectangles_filled_with_colors(points.tolist(), colors)
        shape_list.append(shape)
        shape_list.draw()
