from time import perf_counter_ns as now, sleep
import numpy as np

from .window import Window
from .state import State
from .world.world import World
from .utils import toMs
from .camera import Camera

state = State()
    
def realtime_simulation():

    window = Window()
    state.window = window

    camera = Camera(window.window_size, window.window_size / 2)
    state.camera = camera

    world = World(window)
    state.world = world
    world.populate_world(100)

    state.last_draw = now()
    state.last_tick = now()

    with window:

        while window.running:
            
            state.t = now()
            state.dDraw = toMs(state.t - state.last_draw)
            world.draw(window.surface)
            t_draw = now()
            state.last_draw = t_draw
            
            if (t_draw - state.last_tick) >= state.dTick_target:
                state.dTick = toMs(now() - state.last_tick)
                world.tick()
                camera.tick()
                state.last_tick = now()
                

            sleep(0.002)

    



if __name__ == "__main__":

    realtime_simulation()
