from time import perf_counter_ns as now, sleep
import numpy as np

from .window import Window
from .state import State

state = State()

def tick():

    for entity in state.entities:
        entity.tick()
    

def realtime_simulation():

    window = Window()
    state.window = window
    
    state.last_draw = now()
    state.last_tick = now()

    from .entities.test import TestAgent
    state.entities.append(TestAgent(np.random.random(2) * state.window.window_size))

    with window:

        while window.running:
            
            state.t = now()
            state.dDraw = state.t - state.last_draw
            window.draw()
            t_draw = now()
            state.last_draw = t_draw
            
            
            if (t_draw - state.last_tick) >= state.dTick_target:
                state.dTick = now() - state.last_tick
                tick()
                state.last_tick = now()
                

            sleep(0.002)

            

            



if __name__ == "__main__":

    realtime_simulation()
