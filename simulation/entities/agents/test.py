import numpy as np
import pygame

from .agent import Agent

from ..utils import s
from ..state import State
from ..animations.lerp import lerp

state = State()

class TestAgent(Agent):

    def __init__(self, position: np.ndarray) -> None:
        super().__init__(position)

        self.moving = False

    def draw(self, surface: pygame.Surface):
        pygame.draw.circle(surface, (255, 255, 255), self.position, 10)


    def move_anim(self, pos: np.ndarray):
        self.position = pos

    def tick(self):
        super().tick()

        if not self.moving:
            self.animations.append(lerp(
                self.position,
                np.random.random(2) * state.window.window_size,
                s(0.8),
                self.move_anim
            ))
            self.moving = True

        
        
        