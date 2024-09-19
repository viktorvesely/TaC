from typing import Self
import pygame
import numpy as np

from .state import State

state = State()

class Window:

    # Define window size using numpy array [width, height]
    window_size: np.ndarray = np.array([1000, 600])

    def __init__(self):

        self.running: bool = False
        self.surface: pygame.Surface | None = None

    def __enter__(self) -> Self:

        pygame.init()   # Initialize pygame modules 
        
        # Create pygame window
        self.surface = pygame.display.set_mode(self.window_size)
        self.running = True # Window now running

        return self
    
    def __exit__(
            self,
            exc_type: type[BaseException] | None,
            exc_value: BaseException | None,
            traceback: object | None
        ):

        # Stop window and release resources before quitting
        self.running = False
        self.surface = None

        pygame.quit()
    
    def pygame_event_handler(self):

        state.keys_pressed.clear()

        # Close window input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                state.keys_pressed.add(event.key)



if __name__ == "__main__":

    window = Window()

    with window:

        while window.running:
            window.draw()