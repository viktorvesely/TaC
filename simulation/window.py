from typing import Self
import pygame
import numpy as np

from .state import State

class Window:

    # Define window size using numpy array [width, height]
    window_size: np.ndarray = np.array([1200, 600])

    def __init__(self, state: State):


        self.state = state
        self.running: bool = False
        self.surface: pygame.Surface | None = None
        self.menu_expanded: bool = False

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

        self.state.keys_pressed.clear()

        # Close window input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                self.state.keys_pressed.add(event.key)


            if event.type == pygame.MOUSEBUTTONDOWN:

                mouse_pos = np.array(pygame.mouse.get_pos()).astype(float)
                world_mouse_pos = self.state.camera.screenToWorld @ mouse_pos

                deltas = self.state.agent_position - world_mouse_pos[np.newaxis, :]
                distances = np.linalg.norm(deltas, axis=1)
                i_min_dist = np.argmin(distances)
                min_dist = distances[i_min_dist]

                if min_dist <= self.state.vars.agent_size:
                    self.state.debug_i_agent_print_action = i_min_dist
                else:
                    self.state.debug_i_agent_print_action = -1
            






if __name__ == "__main__":

    window = Window()

    with window:

        while window.running:
            window.draw()