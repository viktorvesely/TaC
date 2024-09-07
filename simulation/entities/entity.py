
import pygame.surface

class Entity:

    def tick(self):
        ...

    def draw(self, surface: pygame.Surface):
        ...
    
    def animate(self):
        ...