from pathlib import Path

def ms(t_ms: float) -> int:
    return int(t_ms * (10 ** 6))

def s(t_s: float) -> int:
    return int(t_s * (10 ** 9))

class Utils:

    @staticmethod 
    def package_path() -> Path:
        return Path(__file__).parent

    @staticmethod
    def experiments_path() -> Path:
        return Utils.package_path() / "data" / "experiments"
    
