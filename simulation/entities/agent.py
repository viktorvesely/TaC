import numpy as np

from .entity import Entity
from ..animations.animation import Animation


class Agent(Entity):


    def __init__(self, position: np.ndarray) -> None:
        self.position: np.ndarray = position
        self.animations: list[Animation] = [] 


    def animate(self):
        
        # Iterate backwards for safe removal
        for i in range(len(self.animations) - 1, -1, -1):
            animation = self.animations[i]

            # Progress the animation
            _, continue_animating = next(animation)

            if not continue_animating:
               self.animations.pop(i) 

        
                


