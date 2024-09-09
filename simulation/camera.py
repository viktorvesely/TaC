import numpy as np
import pygame

class CameraMatrix:
    __slots__ = ('m',)

    def __init__(self, m: np.ndarray) -> None:
        self.m = m

    def __matmul__(self, p: np.ndarray) -> np.ndarray:
        p = [p[0], p[1], 1]
        projected = self.m @ p
        return projected[:-1]

class Camera:

    camera_speed: float = 5
    zoom_speed_factor: float = 1.05 

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


    def moveBy(self, by: np.ndarray):
        self.position = self.position + by
        self.update()

    def zoomBy(self, by: float):
        self.zoom *= by
        self.update()

    def tick(self):
        
        keys = pygame.key.get_pressed()

        translate = np.zeros(2)
        should_update = False
        zoomBy = 1

        if keys[pygame.K_LEFT]:
            should_update = True
            translate += np.array([-1, 0])
        if keys[pygame.K_RIGHT]:
            should_update = True
            translate += np.array([1, 0])
        if keys[pygame.K_UP]:
            should_update = True
            translate += np.array([0, -1])
        if keys[pygame.K_DOWN]:
            should_update = True
            translate += np.array([0, 1])

        if keys[pygame.K_o]:
            should_update = True
            zoomBy = self.zoom_speed_factor
        if keys[pygame.K_p]:
            should_update = True
            zoomBy = 1 / self.zoom_speed_factor


        if should_update:
            mag = np.linalg.norm(translate)

            if mag != 0:
                translate = translate / mag
                translate = translate * self.camera_speed / self.zoom
            
            self.moveBy(translate)
            self.zoomBy(zoomBy)
            

