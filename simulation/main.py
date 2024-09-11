from time import perf_counter_ns as now, sleep
import arcade
import numpy as np

from .test import GameWindow
from .state import State
from .world.world import World
from .utils import ms, s, toMs
from .camera import Camera

state = State()

def realtime_simulation():

    window = GameWindow(realtime_simulation_cycle, simulation_draw)
    state.window = window

    camera = Camera(window.window_size, np.zeros(2))
    state.camera = camera

    world = World(window)
    state.world = world

    state.last_draw = now()
    state.last_tick = now()

    window.run()

    # with window:

    #     while window.running:

    #         window.pygame_event_handler()

    #         if pygame.K_p in state.keys_pressed:
    #             paused = not paused

    #         if paused:
    #             paused_simulation_cycle(window, camera, world)
    #         else:
    #             realtime_simulation_cycle(window, camera, world)

    #         sleep(0.005)

def simulation_draw():

    state.world.grid.draw()
    state.world.agents.draw()

def realtime_simulation_cycle():

    if state.paused:
        paused_simulation_cycle()
    else:
        unpaused_simulation_cycle()
    

def paused_simulation_cycle():
    
    d = toMs(state.dTick_target)
    state.t = now()
    
    state.camera.tick()
    
    if arcade.key.BRACKETLEFT in state.keys_pressed:
        state.dTick = d
        state.world.tick()

    state.last_tick = state.t
        

def unpaused_simulation_cycle():
    
    state.camera.tick()
    state.t = now()
    state.dTick = toMs(now() - state.last_tick)
    state.world.tick()
    state.last_tick = now()


if __name__ == "__main__":


    if True:
        realtime_simulation()
    else:
        import pstats, cProfile

        # Use the with statement to profile the function and save the results to a file
        with cProfile.Profile() as profiler:
            realtime_simulation()

        # Create a Stats object from the saved profile results
        stats = pstats.Stats(profiler)

        # Sort the statistics by cumulative time and print them
        stats.sort_stats('cumulative')
        stats.dump_stats(filename="profile.prof")

    
