
import pygame.surface
from abc import ABC, abstractmethod

class Entity(ABC):

    @abstractmethod
    def tick(self):
        ...

    @abstractmethod
    def draw(self, surface: pygame.Surface):
        ...
    