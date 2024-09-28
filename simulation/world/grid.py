import numpy as np
from pygame import Surface, draw, Rect
import pygame

from ..entities.entity import Entity
from ..entities.agents.agent import Agent
from ..state import State

state = State() # Singleton for accessing state of game or simulation

WPOS_TL = 0     # Top left placement
WPOS_MIDDLE = 1 # Middle placement

class Grid:     # 2D grid world, handles spatial positioning, wall locations, and drawing of grid and walls

    def __init__(self, walls: np.ndarray, size: float = 40) -> None:

        self.walls = walls
        self.walkable_mask = np.isclose(walls, 0.0)
        n_grids = walls.shape[0]

        if (n_grids % 2) != 0:
            raise ValueError("N grids needs to be divisible by 2") 

        self.size = size # Cell size in grid
        self._tomid: np.ndarray = np.ones(2) * (self.size / 2) # Offset to get cell center
        self.world_size = np.array([-size, size], dtype=np.float64) * (n_grids / 2) # World size
        self.world_TL = np.array([-size, -size], dtype=np.float64) * (n_grids / 2) # Top left corner of world
        self.ngrids = n_grids

        self.grid_indicies = np.empty((self.ngrids, self.ngrids), dtype=object)
        for i in range(self.ngrids):
            for j in range(self.ngrids):
                self.grid_indicies[i, j] = (i, j)

        self.density: np.ndarray = np.zeros_like(self.walls, dtype=np.int32)
        self.offsets: np.ndarray = np.zeros_like(self.walls, dtype=np.int32)
        self.homogenous_indicies: np.ndarray | None = None 
        self.register_agent_coords()

    

    def world_pos_to_cell_pos(self, pos: np.ndarray) -> tuple[int, int]: # World coordinates to grid cell coordinates conversion
        pos = pos - self.world_TL
        return int(pos[1] // self.size), int(pos[0] // self.size)
    
    def cell_pos_to_world_pos(self, pos: tuple[int, int], placement: int = WPOS_TL) -> np.ndarray: # Grid cell position to world coordinates conversion
        out = np.array([pos[1], pos[0]]) * self.size + self.world_TL

        if placement == WPOS_MIDDLE:
            out = out + self._tomid
        
        return out
    
    def vectorized_world_to_cell(self, positions: np.ndarray) -> np.ndarray: # Multiple world positions to grid cell positions
        """
        positions (n_entities, 2)
        """
        positions = positions - self.world_TL
        coords = (positions // self.size).astype(int)
        return np.flip(coords, axis=1)

    def vectorized_cell_to_world(self, coords: np.ndarray, placement: int = WPOS_TL) -> np.ndarray: # Multiple grid cell positions to world positions
        out = (np.flip(coords, axis=1)).astype(float) * self.size + self.world_TL

        if placement == WPOS_MIDDLE:
            out = out + self._tomid
        
        return out

    def draw_grid(self, surface: Surface): # Draw grid lines on surface using camera's view
        camera = state.camera
        w_min, w_max = self.world_size

        # Get visible area in world coordinates
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

    def get_walls_inds_from_to(self, top_left: np.ndarray, bottom_right: np.ndarray) -> tuple[int, int, int, int]:

        # Get indices of walls within rectangular area in the grid
        top, left = self.world_pos_to_cell_pos(top_left)
        bottom, right = self.world_pos_to_cell_pos(bottom_right)

        # Include the outer layer
        left += -1
        right += 1
        top += -1
        bottom += 1

        left = max(0, left)
        right = max(0, right)
        top = max(0, top)
        bottom = max(0, bottom)

        return left, right, top, bottom

    def draw_walls(self, surface: Surface):
        
        # Draw walls on surface based on camera view
        camera = state.camera
        top_left = camera.screenToWorld @ np.zeros(2)
        bottom_right = camera.screenToWorld @ state.window.window_size

        left, right, top, bottom = self.get_walls_inds_from_to(top_left, bottom_right)
        w, i = self.walls[top:bottom, left:right], self.grid_indicies[top:bottom, left:right]

        wall_mask = np.isclose(w, 1.0)
        wall_inds = np.where(wall_mask)

        for local_i, local_j in zip(*wall_inds):
            world_pos = self.cell_pos_to_world_pos(i[local_i, local_j])
            screen_pos = camera.worldToScreen @ world_pos
            side = int(self.size * camera.zoom)
            draw.rect(
                surface,
                (255, 255, 255),
                Rect(int(screen_pos[0]), int(screen_pos[1]), side, side),
                width=int(max(1, 3 * camera.zoom))
            )
        

    @classmethod
    def extract_ent_pos(cls, ents: list[Entity]) -> np.ndarray:
        positions = [ent.position for ent in ents]
        return np.array(positions)
    
    @classmethod
    def inject_ent_pos(cls, ents: list[Entity], positions: np.ndarray): # Update positions of all entities
        for i, ent in enumerate(ents):
            ent.position = positions[i, :]

    def handle_wall_collision(self):


        ent_pos = state.agent_position
        n_ents = ent_pos.shape[0]

        # Extract cell info given particle
        cell_inds = self.vectorized_world_to_cell(ent_pos)
        cell_pos = self.vectorized_cell_to_world(cell_inds, placement=WPOS_MIDDLE)

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
        state.agent_position = ent_pos

    def register_agent_coords(self):

        agent_coords = state.agent_coords if state.agent_coords is not None else self.vectorized_world_to_cell(state.agent_position)
        i, j = agent_coords.T
        self.density = np.zeros((self.ngrids, self.ngrids), dtype=np.int32)
        np.add.at(self.density, (i, j), 1.0)

        self.offsets = np.cumsum(
            np.pad(self.density.flatten(), (1, 0))
        )[:-1].reshape(self.density.shape).astype(np.int32)

        self.homogenous_indicies = np.lexsort((agent_coords[:, 1], agent_coords[:, 0])).astype(np.int32)

    
    def tick(self):

        state.agent_position = np.clip(state.agent_position, *(self.world_size + np.array([10, -10])))
        self.handle_wall_collision()
        state.agent_position = np.clip(state.agent_position, *(self.world_size + np.array([10, -10])))

        self.register_agent_coords()
        
            

    def draw(self, surface: Surface):

        keys = pygame.key.get_pressed()

        if keys[pygame.K_l]:
            self.draw_grid(surface)

        self.draw_walls(surface)

        # print(self.world_pos_to_cell_pos(state.camera.screenToWorld @ np.array(pygame.mouse.get_pos())))
