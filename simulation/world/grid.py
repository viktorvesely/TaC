import numpy as np
from pygame import Surface, draw

from ..state import State

state = State()

class Grid:

    def __init__(self, size: float = 30) -> None:
        
        self.size = size
        self.origin: np.ndarray = np.zeros(2)

    
    def draw(self, surface: Surface):

        draw_width = state.window.window_size