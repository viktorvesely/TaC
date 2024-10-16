from typing import Self
import pygame
import numpy as np
import pygame_gui

from .state import State

class Window:

    # Define window size using numpy array [width, height]
    window_size: np.ndarray = np.array([1200, 600])

    def __init__(self, state: State):


        self.state = state
        self.running: bool = False
        self.surface: pygame.Surface | None = None
        self.manager: pygame_gui.UIManager | None = None
        self.menu_expanded: bool = False

    def __enter__(self) -> Self:

        pygame.init()   # Initialize pygame modules 
        
        # Create pygame window
        self.surface = pygame.display.set_mode(self.window_size)
        self.manager = pygame_gui.UIManager(self.window_size)
        self.running = True # Window now running

        # Create a button that will act as the menu toggle
        self.menu_toggle_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((50, 50), (100, 50)),
            text='Menu',
            manager=self.manager
        )

        # Create the menu elements but hide them initially
        self.slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect((50, 110), (200, 50)),
            start_value=0,
            value_range=(0, 100),
            manager=self.manager
        )
        self.slider.hide()



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

            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                
                if event.ui_element == self.menu_toggle_button:
                    # Toggle the visibility of the menu elements
                    self.menu_expanded = not self.menu_expanded

                    if self.menu_expanded:
                        self.slider.show()
                    else:
                        self.slider.hide()

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
            
            self.manager.process_events(event)

        self.manager.update(self.state.dTick / 2000)





if __name__ == "__main__":

    window = Window()

    with window:

        while window.running:
            window.draw()