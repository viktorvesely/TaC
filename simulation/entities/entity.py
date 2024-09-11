
import numpy as np
from abc import ABC, abstractmethod

class Entity(ABC):

    def __init__(self, positon: np.ndarray) -> None:
        super().__init__()

        self.position: np.ndarray = positon

    @abstractmethod
    def tick(self):
        ...

    @abstractmethod
    def draw(self, surface):
        ...
    