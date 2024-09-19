from pathlib import Path

import numpy as np

def ms(t_ms: float) -> int:
    # Converts time in milliseconds to nanoseconds
    return int(t_ms * (10 ** 6))

def s(t_s: float) -> int:
    # Converts seconds to nanoseconds
    return int(t_s * (10 ** 9))

def toMs(ns: int) -> float:
    # Converts nanoseconds to milliseconds
    return ns / (10 ** 6)

class Utils:

    @staticmethod 
    def package_path() -> Path:
        # Returns path to the current file's directory
        return Path(__file__).parent

    @staticmethod
    def experiments_path() -> Path:
        # Returns path to the 'data/experiments' folder inside the package
        return Utils.package_path() / "data" / "experiments"
    
    @staticmethod
    def vectorized_projection(matrix: np.ndarray, points: np.ndarray) -> np.ndarray:
        
        additive = np.ones((points.shape[0], 3))
        additive[:, :2] = points
        
        projected = (matrix @ additive.T).T
        return projected[:, :2]
