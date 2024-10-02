from .agent import Agent

import numpy as np
from pygame import Surface
import pygame

class Citizen(Agent):
    def __init__(self, number_cit:int):
        super().__init__(number_cit)
        self.role = "citizen"
        self.color = np.array([0, 255, 0])
        
    def behaviour(self):
        # Define citizen's behavior
        print("I am a citizen")
        
    def draw(self, surface: Surface):
        
        additive = np.ones((self.n, 3))
        additive[:, :2] = self.position
    
        projected = self.state.camera.worldToScreen.m @ additive.T
        projected = projected[:2, :].T

        for position in projected:
            pygame.draw.circle(surface, self.color, position, 10 * self.state.camera.zoom)