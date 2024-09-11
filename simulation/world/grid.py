import arcade
import arcade.color
import numpy as np

from ..entities.entity import Entity
from ..state import State
from ..utils import Utils

state = State()

WPOS_TL = 0
WPOS_MIDDLE = 1

class Grid:

    def __init__(self, size: float = 40, grid_size: int = 40) -> None:
        
        self.size = size
        self._tomid: np.ndarray = np.ones(2) * (self.size / 2)
        self.world_size = np.array([-size, size]) * grid_size
        self.world_TL = np.array([-size, -size]) * grid_size
        self.ngrids = grid_size * 2

        self.walls = np.random.choice([1.0, 0.0], p=[0.2, 0.8], size=(self.ngrids, self.ngrids))
        # self.walls = np.zeros((self.ngrids, self.ngrids))
        # self.walls[0, :] = 1.0

        wall_mask = ~np.isclose(self.walls, 0)
        wall_inds = np.array(np.where(wall_mask)).T
        wall_positions = self.vectorized_cell_to_world(wall_inds, placement=WPOS_MIDDLE)
        self.wall_mesh: np.ndarray = Utils.create_proojected_rect_mesh_array(
            centers=wall_positions,
            positive_offset_size=np.array([self.size, self.size]) / 2
        )

        self._indicies = np.empty((self.ngrids, self.ngrids), dtype=object)    
        for i in range(self.ngrids):
            for j in range(self.ngrids):
                self._indicies[i, j] = (j, i)

        
    

    def world_pos_to_cell_pos(self, pos: np.ndarray) -> tuple[int, int]:
        pos = pos - self.world_TL
        return int(pos[0] // self.size), int(pos[1] // self.size)
    
    def cell_pos_to_world_pos(self, pos: tuple[int, int], placement: int = WPOS_TL) -> np.ndarray:
        out = np.array(pos) * self.size + self.world_TL

        if placement == WPOS_MIDDLE:
            out = out + self._tomid
        
        return out
    
    def vectorized_world_to_cell(self, positions: np.ndarray) -> np.ndarray:
        """
        positions (n_entities, 2)
        """
        positions = positions - self.world_TL
        return (positions // self.size).astype(int)

    def vectorized_cell_to_world(self, positions: np.ndarray, placement: int = WPOS_TL) -> np.ndarray:
        out = (positions).astype(float) * self.size + self.world_TL

        if placement == WPOS_MIDDLE:
            out = out + self._tomid
        
        return out

    def draw_grid(self, surface):
        camera = state.camera
        w_min, w_max = self.world_size

        top_left = camera.screenToWorld @ np.zeros(2)
        top_left = np.clip(top_left, w_min, w_max)
        bottom_right = camera.screenToWorld @ state.window.window_size
        bottom_right = np.clip(bottom_right, w_min, w_max)

        # Calculate the range of the visible area in world coordinates
        start_x = (top_left[0] // self.size) * self.size
        end_x = (bottom_right[0] // self.size) * self.size
        start_y = (top_left[1] // self.size) * self.size
        end_y = (bottom_right[1] // self.size) * self.size

        # Draw vertical lines
        x = start_x
        while (x <= end_x) and (w_min <= x <= w_max):
            screen_start = camera.worldToScreen @ np.array([x, top_left[1]])
            screen_end = camera.worldToScreen @ np.array([x, bottom_right[1]])
            draw.line(surface, (255, 255, 255), screen_start, screen_end)
            x += self.size

        # Draw horizontal lines
        y = start_y
        while (y <= end_y) and (w_min <= y <= w_max):
            screen_start = camera.worldToScreen @ np.array([top_left[0], y])
            screen_end = camera.worldToScreen @ np.array([bottom_right[0], y])
            draw.line(surface, (255, 255, 255), screen_start, screen_end)
            y += self.size

    def draw_walls(self):
        
        camera = state.camera

        # wall_mask = ~np.isclose(self.walls, 0)
        # wall_inds = np.array(np.where(wall_mask)).T
        # wall_positions = self.vectorized_cell_to_world(wall_inds, placement=WPOS_MIDDLE)
        # wall_mesh: np.ndarray = Utils.create_proojected_rect_mesh_array(
        #     centers=wall_positions,
        #     positive_offset_size=np.array([self.size, self.size]) / 2.0,
        #     worldToScreen=camera.worldToScreen.m
        # )

        wall_mesh = Utils.vectorized_projection(camera.worldToScreen.m, self.wall_mesh)
        n_verticies = wall_mesh.shape[0]

        colors = np.repeat(np.array(arcade.color.WHITE)[np.newaxis, :], n_verticies, axis=0)

        shape_list = arcade.ShapeElementList()
        shape = arcade.create_rectangles_filled_with_colors(wall_mesh, colors)
        shape_list.append(shape)
        shape_list.draw()


        # for y_i, x_i in zip(*wall_inds):
        #     world_pos = self.cell_pos_to_world_pos(i[y_i, x_i], placement=WPOS_MIDDLE)
        #     screen_pos = camera.worldToScreen @ world_pos
        #     side = self.size * camera.zoom
        #     arcade.draw_rectangle_outline(
        #         *screen_pos,
        #         side, side,
        #         (255, 255, 255),
        #         border_width=int(max(1, 3 * camera.zoom))
        #     )

    def draw(self):

        # if arcade.key.L in state.keys_pressing:
        #     self.draw_grid(surface)

        mid = state.camera.worldToScreen @ np.array([0, 0])
        side = self.world_size[1] * state.camera.zoom * 2
        arcade.draw_rectangle_outline(*mid, side, side, arcade.color.WHITE)

        self.draw_walls()

        # self.draw_walls(surface)

        # print(self.world_pos_to_cell_pos(state.camera.screenToWorld @ np.array(pygame.mouse.get_pos())))
        

    @classmethod
    def extract_ent_pos(cls, ents: list[Entity]) -> np.ndarray:
        positions = [ent.position for ent in ents]
        return np.array(positions)
    
    @classmethod
    def inject_ent_pos(cls, ents: list[Entity], positions: np.ndarray):
        for i, ent in enumerate(ents):
            ent.position = positions[i, :]



    def handle_wall_collision(self):


        ent_pos = state.agent_positions # self.extract_ent_pos(collider_entities)
        n_ents = ent_pos.shape[0]

        # Collision with map bound
        ent_pos = np.clip(ent_pos, *(self.world_size + np.array([1, -1])))

        # Extract cell info given particle
        cell_inds = self.vectorized_world_to_cell(ent_pos)
        cell_pos = self.vectorized_cell_to_world(cell_inds, placement=WPOS_MIDDLE)

        # TODO flip should not happen here, fix this : (
        # wall_inds = tuple(np.flip(cell_inds.T, axis=0))
        wall_inds = tuple(cell_inds.T)

        wall_value = self.walls[wall_inds]
        collide_mask = ~np.isclose(wall_value, 0.0)

        n_collide_ents = collide_mask.sum()
        if n_collide_ents == 0:
            return

        # Collision
        collision_cell_pos = cell_pos[collide_mask]
        collision_ent_pos = ent_pos[collide_mask]

        # Find the point closest poin on the cell border to the ent
        collision_cell_TL = collision_cell_pos - self._tomid
        collision_cell_BR = collision_cell_pos + self._tomid 

        collision_potential_points = np.empty((4, n_collide_ents, 2))
        collision_potential_points[0, :, :] = np.vstack((collision_ent_pos[:, 0], collision_cell_TL[:, 1])).T
        collision_potential_points[1, :, :] = np.vstack((collision_ent_pos[:, 0], collision_cell_BR[:, 1])).T
        collision_potential_points[2, :, :] = np.vstack((collision_cell_TL[:, 0], collision_ent_pos[:, 1])).T
        collision_potential_points[3, :, :] = np.vstack((collision_cell_BR[:, 0], collision_ent_pos[:, 1])).T

        # Find the closest collision point given 4 potential points
        collision_potential_distances = np.linalg.norm(collision_potential_points - collision_ent_pos[np.newaxis, :, :], axis=2)
        collision_closest_indices = np.argmin(collision_potential_distances, axis=0)
        collision_closest_points = collision_potential_points[collision_closest_indices, np.arange(n_collide_ents)]

        # Resolve the collision using the collision point
        ent_pos[collide_mask] = collision_closest_points

        state.agent_positions = ent_pos  #self.inject_ent_pos(collider_entities, ent_pos)

    def tick(self):
        self.handle_wall_collision()
            
