from pathlib import Path

import numpy as np

def ms(t_ms: float) -> int:
    return int(t_ms * (10 ** 6))

def s(t_s: float) -> int:
    return int(t_s * (10 ** 9))

def toMs(ns: int) -> float:
    return ns / (10 ** 6)

class Utils:

    @staticmethod 
    def package_path() -> Path:
        return Path(__file__).parent

    @staticmethod
    def experiments_path() -> Path:
        return Utils.package_path() / "data" / "experiments"
    
    @staticmethod
    def vectorized_projection(
        projection: np.ndarray,
        points: np.ndarray
    ) -> np.ndarray:
        
        additive = np.ones((points.shape[0], 3))
        additive[:, :2] = points
        projected = projection @ additive.T
        return projected[:2, :].T
        

    @staticmethod
    def create_proojected_rect_mesh_array(
        centers: np.ndarray,
        positive_offset_size: np.ndarray,
        worldToScreen: np.ndarray | None = None
    ) -> np.ndarray:

        worldToScreen = np.identity(3) if worldToScreen is None else worldToScreen

        offset = positive_offset_size
        offset2 = np.array([-offset[0], offset[1]])

        TL = centers + offset2
        TR = centers + offset
        BR = centers - offset2
        BL = centers - offset

        point_groups = [TL, TR, BR, BL]
        point_groups = [Utils.vectorized_projection(worldToScreen, points) for points in point_groups]
        point_groups = np.array(point_groups).reshape((-1, 2), order="F")

        return point_groups
    

