import numpy as np
from pygame import Surface, draw

from ..state import State

state = State()

class Grid:

    def __init__(self, size: float = 100, grid_size: int = 30) -> None:
        
        self.size = size
        self.world_size = np.array([-size, size]) * grid_size

    
    def draw(self, surface: Surface):

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

