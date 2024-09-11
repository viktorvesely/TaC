import time
from typing import Callable
import arcade
from arcade.experimental.texture_render_target import RenderTargetTexture
import arcade.key
import numpy as np

from .state import State

state = State()


class GPURenderTexture(RenderTargetTexture):
    def __init__(self, width, height):
        super().__init__(width, height)
        self.program = self.ctx.program(
            vertex_shader="""
            #version 330

            in vec2 in_vert;
            in vec2 in_uv;
            out vec2 uv;

            void main() {
                gl_Position = vec4(in_vert, 0.0, 1.0);
                uv = in_uv;
            }
            """,
            fragment_shader="""
            #version 330

            uniform sampler2D texture0;

            in vec2 uv;
            out vec4 fragColor;

            void main() {
                vec4 color = texture(texture0, uv);

                fragColor = vec4(0.0);
            }
            """,
        )

    def use(self):
        self._fbo.use()

    def draw(self):
        self.texture.use(0)
        self._quad_fs.render(self.program)


class GameWindow(arcade.Window):

    window_size: np.ndarray = np.array([1000, 700])

    def __init__(self, simulation_cycle: Callable, simulation_draw: Callable):
        super().__init__(*self.window_size, "TaC")
        self.filter = GPURenderTexture(*self.window_size)
        self.simulation_cycle = simulation_cycle
        self.simulation_draw = simulation_draw

    def on_draw(self):
        self.clear()
        self.filter.clear()
        self.filter.use()

        self.use()
        self.filter.draw()
        self.simulation_draw()


    def on_update(self, delta_time: float):
        
        if arcade.key.X in state.keys_pressed:
            self.close()

        self.simulation_cycle()

        state.keys_pressed.clear()

    def on_key_press(self, symbol: int, modifiers: int):
        super().on_key_press(symbol, modifiers)

        state.keys_pressed.add(symbol)
        state.keys_pressing.add(symbol)

    def on_key_release(self, symbol: int, modifiers: int):
        super().on_key_release(symbol, modifiers)
        
        state.keys_pressing.remove(symbol)
        