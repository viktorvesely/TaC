import numpy as np
import arcade.key as key

from .state import State

state = State()

class CameraMatrix:
    __slots__ = ('m',)

    def __init__(self, m: np.ndarray) -> None:
        self.m = m

    def __matmul__(self, p: np.ndarray) -> np.ndarray:
        p = [p[0], p[1], 1]
        projected = self.m @ p
        return projected[:-1]

class Camera:

    camera_speed: float = 4
    zoom_speed_factor: float = 1.016 
    min_zoom: float = 0.11
    max_zoom: float = 5.0

    def __init__(self, window_size: np.ndarray, positon: np.ndarray, zoom: float = 1.0) -> None:
        
        self.position = positon
        self.zoom = zoom

        self._window_shift: np.ndarray = np.array([
            [1, 0, window_size[0] / 2],
            [0, 1, window_size[1] / 2],
            [0, 0, 1]
        ])

        self.worldToScreen: CameraMatrix = None
        self.screenToWorld: CameraMatrix = None
        self.update()

    def update(self):

        translation = np.array([
            [1, 0, -self.position[0]],
            [0, 1, -self.position[1]],
            [0, 0, 1]
        ])

        scaling = np.array([
            [self.zoom, 0, 0],
            [0, self.zoom, 0],
            [0, 0, 1]
        ])

        self.worldToScreen = CameraMatrix(self._window_shift @ scaling @ translation)
        self.screenToWorld = CameraMatrix(np.linalg.inv(self.worldToScreen.m))


    def moveBy(self, by: np.ndarray, _update: bool=True):
        self.position = self.position + by
        
        if _update:
            self.update()

    def zoomBy(self, by: float, _update: bool=True):
        self.zoom *= by
        self.zoom = max(self.min_zoom, min(self.max_zoom, self.zoom))

        if _update:
            self.update()

    def tick(self):
    
        pressing = state.keys_pressing

        translate = np.zeros(2)
        should_update = False
        zoomBy = 1
        speed_boost = 1

        if key.A in pressing:
            should_update = True
            translate += np.array([-1, 0])
        if key.D in pressing:
            should_update = True
            translate += np.array([1, 0])
        if key.W in pressing:
            should_update = True
            translate += np.array([0, 1])
        if key.S in pressing:
            should_update = True
            translate += np.array([0, -1])

        if key.LSHIFT in pressing:
            speed_boost = 2

        if key.I in pressing:
            should_update = True
            zoomBy = self.zoom_speed_factor
        if key.O in pressing:
            should_update = True
            zoomBy = 1 / self.zoom_speed_factor


        if should_update:
            mag = np.linalg.norm(translate)

            if mag != 0:
                translate = translate / mag
                translate = translate * self.camera_speed * speed_boost / self.zoom
            
            self.moveBy(translate, _update=False)
            self.zoomBy(zoomBy)
            

