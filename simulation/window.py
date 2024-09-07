from typing import Self
import pygame
import numpy as np

from .state import State

state = State()

class Window:

    window_size: np.ndarray = np.array([1000, 800])

    def __init__(self):

        self.running: bool = False
        self.surface: pygame.Surface | None = None

    def __enter__(self) -> Self:

        pygame.init()
        
        self.surface = pygame.display.set_mode(self.window_size)
        self.running = True

        return self
    
    def __exit__(
            self,
            exc_type: type[BaseException] | None,
            exc_value: BaseException | None,
            traceback: object | None
        ):


        self.running = False
        self.surface = None

        pygame.quit()
    
    def pygame_event_handler(self):

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False




if __name__ == "__main__":

    window = Window()

    with window:

        while window.running:
            window.draw()