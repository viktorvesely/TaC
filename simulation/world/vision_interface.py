from pathlib import Path
import numpy as np
from pygame import Rect, Surface
import pygame
from ..state import State
from .grid import Grid
from .c_vision.vision import generate_vision_field

state = State()

class Vision:

    # Attributes to define fov, vision lenght and number or rays
    fov = np.pi / 3         # 60° FOV
    vision_length = 160.0   # Max distance
    n_rays = 5

    def __init__(self, grid: Grid) -> None:
        
        self.grid = grid
        self.values = np.zeros_like(self.grid.walls)


    def draw_vision_map(self, surface: Surface):
        
        camera = state.camera
        top_left = camera.screenToWorld @ np.zeros(2)
        bottom_right = camera.screenToWorld @ state.window.window_size

        # Get indices of walls in FOV
        left, right, top, bottom = self.grid.get_walls_inds_from_to(top_left, bottom_right)
        v, i = self.values[top:bottom, left:right], self.grid.grid_indicies[top:bottom, left:right]

        vision_mask = ~np.isclose(v, 0)
        vision_inds = np.where(vision_mask)

        # Loop through visible cells and draw rectangles for them
        for local_i, local_j in zip(*vision_inds):
            world_pos = self.grid.cell_pos_to_world_pos(i[local_i, local_j])
            screen_pos = camera.worldToScreen @ world_pos
            side = int(self.grid.size * camera.zoom)
            vision = v[local_i, local_j]
            pygame.draw.rect(
                surface,
                (int(255 * vision), 0, 0),
                Rect(int(screen_pos[0]), int(screen_pos[1]), side, side),
                width=int(max(1, 3 * camera.zoom))
            )

    # Method to manage drawing of vision maps based on keyboard input
    def draw(self, surface: Surface):
        
        keys = pygame.key.get_pressed()

        if not keys[pygame.K_x]:
            self.draw_vision_map(surface)

    # Update vision field
    def tick(self):
        self.values = generate_vision_field(
            state.agent_position,
            state.agent_angle,
            self.grid.walls,
            self.grid.density,
            self.grid.world_TL,
            self.grid.size,
            self.vision_length,
            self.fov,
            self.n_rays
        )

    @classmethod
    def generate_triangles(cls) -> np.ndarray:  # Generate vision triangle for each agent

        pos = state.agent_position

        triangles = np.empty((3, pos.shape[0], 2))
        triangles[0, :, :] = pos

        heading = np.empty_like(pos)
        heading[:, 0] = np.cos(state.agent_angle)
        heading[:, 1] = np.sin(state.agent_angle)

        orthogonal = np.empty_like(heading) 
        orthogonal[:, 0] = heading[:, 1]
        orthogonal[:, 1] = -heading[:, 0]
        orthogonal = orthogonal * cls.vision_spread

        heading_end = pos + heading * cls.vision_length

        triangles[1, :, :] = heading_end + orthogonal
        triangles[2, :, :] = heading_end - orthogonal

        return triangles
    
    @classmethod
    def in_triangle(cls, triangle: np.ndarray, points: np.ndarray) -> np.ndarray: # Check if points are inside of given triangle
        # https://stackoverflow.com/a/14382692/7020366

        p0, p1, p2 = triangle
        px, py = points.T
        p0x, p0y = p0
        p1x, p1y = p1
        p2x, p2y = p2

        # Calculate areas and return boolean mask indicating whether points are inside the triangle
        s = cls.in_triangle_formula_term * (p0y * p2x - p0x * p2y + (p2y - p0y) * px + (p0x - p2x) * py)
        t = cls.in_triangle_formula_term * (p0x * p1y - p0y * p1x + (p0y - p1y) * px + (p1x - p0x) * py)

        return (s > 0) & (t > 0) & ((1 - s - t) > 0)
    
    def update_vision(self):

        triangles = self.generate_triangles()

        top_left = state.agent_position + self.lefttop
        bottom_right = state.agent_position + self.rightbottom

        # I think this can be vectorized
        for i_agent in triangles.shape[1]:
            tl = top_left[i_agent, :]
            br = bottom_right[i_agent, :]
            left, right, top, bottom = self.get_walls_inds_from_to(tl, br)
            
            w = self.grid.walls[top:bottom, left:right].reshape((-1,))
            wpos = self.grid.walls_pos[top:bottom, left:right].reshape((-1, 2))
            indicies = self.grid.grid_indicies[top:bottom, left:right].reshape((-1, 2))

            not_wall_mask = np.isclose(w, 0)
            

    