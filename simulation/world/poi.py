import numpy as np
import pygame
from .grid import Grid
from ..state import State
from ..utils import Utils

state = State()

class PointsOfInterests:

    def __init__(self, grid: Grid) -> None:
        
        self.grid: Grid = grid
        self.coords = np.empty((0, 2), dtype=np.int32)
        

    def add_random(self, N: int = 1):

        empty_mask = np.isclose(self.grid.walls, 0)
        empty_inds = np.where(empty_mask)
        choices = np.random.choice(empty_inds[0].size, size=N, replace=False)
        
        append = []
        for choice in choices:
            i = empty_inds[0][choice]
            j = empty_inds[1][choice]
            append.append([i, j])
            self.grid.walls[i, j] = 2.0
        
        self.coords = np.vstack((self.coords, np.array(append)))


    def draw(self, surface: pygame.Surface):

        positions = self.grid.vectorized_cell_to_world(self.coords)
        screen_positions = Utils.vectorized_projection(state.camera.worldToScreen.m, positions)
        side = int(self.grid.size * state.camera.zoom)
        width = int(max(1, 3 * state.camera.zoom))

        for screen_pos in screen_positions:
            pygame.draw.rect(
                surface,
                (0, 255, 0),
                pygame.Rect(int(screen_pos[0]), int(screen_pos[1]), side, side),
                width=width
            )
