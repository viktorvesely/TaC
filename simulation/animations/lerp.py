
from typing import Callable
import numpy as np

from .animation import Animation

from ..state import State

state = State()

class lerp(Animation[np.ndarray]):

    def __init__(
            self,
            start: np.ndarray,
            end: np.ndarray,
            duration: int,
            on_animation: Callable[[np.ndarray], None] | None = None
        ):

        self.start = start
        self.end = end
        self.duration = duration
        
        self.start_t = state.t

        super().__init__(self.animator(), on_animation)


    def animator(self):

        while (v := (state.t - self.start_t) / self.duration) <= 1.0:
            yield self.start + (self.end - self.start) * v