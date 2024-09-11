import arcade
import arcade.key
import numpy as np

from .state import State

def create_proojected_rect_mesh_array(
        centers: np.ndarray,
        positive_offset_size: np.ndarray,
    ) -> np.ndarray:

        offset = positive_offset_size
        offset2 = np.array([-offset[0], offset[1]])

        TL = centers + offset2
        TR = centers + offset
        BR = centers - offset2
        BL = centers - offset

        point_groups = [TL, TR, BR, BL]
        point_groups = np.array(point_groups).reshape((-1, 2), order="F")

        return point_groups

state = State()

n_agents = 10_000

window_size = np.array([1200, 700])
agent_pos = np.random.random((n_agents, 2)) * window_size
agent_vel = np.zeros((n_agents, 2))
agent_angle = np.random.random(n_agents) * 2 * np.pi

class GameWindow(arcade.Window):

    window_size: np.ndarray = np.array([1000, 700])

    def __init__(self):
        super().__init__(*self.window_size, "TaC")

    def on_draw(self):
        self.clear()
        # self.filter.clear()
        # self.filter.use()

        self.use()
        # self.filter.draw()

        mesh = create_proojected_rect_mesh_array(agent_pos, np.array([10, 10]))
        shape_list = arcade.ShapeElementList()
        colors = np.repeat(np.array(arcade.color.WHITE)[np.newaxis, :], mesh.shape[0], axis=0)
        shape = arcade.create_rectangles_filled_with_colors(mesh, colors)
        shape_list.append(shape)
        shape_list.draw()
        

    def on_update(self, delta_time: float):        
        global agent_angle, agent_pos, agent_vel
        agent_angle = agent_angle + (0.0001 * delta_time) % (np.pi * 2)
        agent_vel = np.vstack((np.cos(agent_angle), np.sin(agent_angle))).T * 3
        agent_pos = agent_pos + agent_vel * delta_time

        print(1 / (delta_time))


if __name__ == "__main__":

    sim = GameWindow()
    sim.run()