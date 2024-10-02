from .agent import Agent
import numpy as np

from pygame import Surface
import pygame


class Thief(Agent):
    def __init__(self, number_thiefs:int):
        super().__init__(number_thiefs)
        self.role = "thief"
        self.color = np.array([255, 0, 0])
        
    def behaviour(self):
        # Thief specific behavior
        print("I am a thief")

    def draw(self, surface: Surface):
        
        additive = np.ones((self.n, 3))
        additive[:, :2] = self.position
    
        projected = self.state.camera.worldToScreen.m @ additive.T
        projected = projected[:2, :].T

        for position in projected:
            pygame.draw.circle(surface, self.color, position, 10 * self.state.camera.zoom)
