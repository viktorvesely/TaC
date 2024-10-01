import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
from time import sleep, perf_counter_ns
import numpy as np
import pygame
import random

from .window import Window
from .state import State, Vars
from .world.world import World
from .utils import toMs
from .camera import Camera
from .events.event import EventManager


main = __name__ == "__main__"

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

    state.last_tick = now()
    state.start_t = now()

    event_manager = EventManager()
    state.event_manager = event_manager

    with window, event_manager:

        while window.running:

            window.pygame_event_handler()

            if pygame.K_p in state.keys_pressed:
                paused = not paused

            if paused:
                paused_simulation_cycle(window, camera, world)
            else:
                realtime_simulation_cycle(window, camera, world)

            sleep((0.002))

    print(state.t - state.start_t)

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

    

def experiment_simulation(config: Vars, desired_t_s: float):

    state.vars = config

    np.random.seed(int.from_bytes(os.urandom(4), byteorder='little'))
    random.seed(int.from_bytes(os.urandom(4), byteorder='little'))

    event_manager = EventManager()
    state.event_manager = event_manager

    state.window = Window()

    world = World(state.window)
    state.world = world

    state.start_t = 0
    state.t = state.start_t
    state.last_tick = state.start_t
    end_t = (desired_t_s * 1000) + state.start_t

    with event_manager:
        while state.t < end_t:
            d = state.dTick_target
            state.t += d
            state.dTick = d 
            world.tick()
            state.last_tick = state.t



if main:

    if True:
        realtime_simulation()
    else:
        import pstats, cProfile

        # Use the with statement to profile the function and save the results to a file
        with cProfile.Profile() as profiler:
            experiment_simulation(Vars(), desired_t_s=120)

        # Create a Stats object from the saved profile results
        stats = pstats.Stats(profiler)

        # Sort the statistics by cumulative time and print them
        stats.sort_stats('cumulative')
        stats.dump_stats(filename="profile.prof")

    
