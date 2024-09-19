from time import sleep, perf_counter_ns
import numpy as np
import pygame

from .window import Window
from .state import State
from .world.world import World
from .utils import toMs
from .camera import Camera


def now():
    return toMs(perf_counter_ns())

state = State()

def realtime_simulation():

    paused = False

    window = Window()
    state.window = window

    camera = Camera(window.window_size, np.zeros(2))
    state.camera = camera

    world = World(window)
    state.world = world

    state.last_draw = now()
    state.last_tick = now()

    with window:

        while window.running:

            window.pygame_event_handler()

            if pygame.K_p in state.keys_pressed:
                paused = not paused

            if paused:
                paused_simulation_cycle(window, camera, world)
            else:
                realtime_simulation_cycle(window, camera, world)

            sleep(0.005)

def paused_simulation_cycle(window: Window, camera: Camera, world: World):

    d = state.dTick_target
    state.t = now()  

    camera.tick()
    
    if pygame.K_RIGHTBRACKET in state.keys_pressed:
        state.dTick = d
        world.tick()

    world.draw(window.surface)

    state.last_tick = state.t
        

def realtime_simulation_cycle(window: Window, camera: Camera, world: World):
    
    camera.tick()

    if not (now() - state.last_tick >= state.dTick_target):
        return
    
    state.t = now()
    state.dTick = state.t - state.last_tick
    world.tick()
    state.last_tick = now()

    world.draw(window.surface)

    



if __name__ == "__main__":

    realtime_simulation()


    if False:
        import pstats, cProfile

        # Use the with statement to profile the function and save the results to a file
        with cProfile.Profile() as profiler:
            realtime_simulation()

        # Create a Stats object from the saved profile results
        stats = pstats.Stats(profiler)

        # Sort the statistics by cumulative time and print them
        stats.sort_stats('cumulative')
        stats.dump_stats(filename="profile.prof")

    
