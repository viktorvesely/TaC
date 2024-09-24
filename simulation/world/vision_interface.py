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
        self.max_targets_per_agent: int = 5


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

        if keys[pygame.K_x]:
            self.draw_vision_map(surface)

    # Update vision field
    def tick(self):
        state.agents_in_vision = np.full((state.n_agents, self.max_targets_per_agent), -1, dtype=np.int32)
        self.values = generate_vision_field(
            state.agent_position,
            state.agent_angle,
            self.grid.walls,
            self.grid.density,
            self.grid.offsets,
            self.grid.homogenous_indicies,
            state.agents_in_vision,
            self.grid.world_TL,
            self.grid.size,
            self.vision_length,
            self.fov,
            self.n_rays
        )


    