from time import perf_counter_ns as now, sleep
import numpy as np
import pygame

from .window import Window
from .state import State
from .world.world import World
from .utils import toMs
from .camera import Camera

state = State()

def realtime_simulation():

    paused = False

    window = Window()
    state.window = window

    camera = Camera(window.window_size, np.zeros(2))
    state.camera = camera

    world = World(window)
    state.world = world
    world.populate_world(100)

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

    d = toMs(state.dTick_target)

    state.t = now()
    state.dDraw = d

    world.draw(window.surface)
    
    state.last_draw = state.t
    
    camera.tick()
    
    if pygame.K_RIGHTBRACKET in state.keys_pressed:
        state.dTick = d
        world.tick()

    state.last_tick = state.t
        

def realtime_simulation_cycle(window: Window, camera: Camera, world: World):
    
    camera.tick()

    if not ((now() - state.last_tick) >= state.dTick_target):
        return
    
    state.t = now()
    state.dDraw = toMs(state.t - state.last_draw)
    world.draw(window.surface)
    t_draw = now()
    state.last_draw = t_draw

    state.dTick = toMs(now() - state.last_tick)
    world.tick()
    state.last_tick = now()

    



if __name__ == "__main__":

    realtime_simulation()
