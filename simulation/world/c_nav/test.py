import numpy as np
from navigation import navigate as cnavigate
import time
from pynav import navigate
import tqdm

# Create a sample grid
height, width = 100, 100
walls = np.random.choice([0.0, 1.0], p=[0.7, 0.3], size=(height, width))

ctime = []
ptime = []

for _ in tqdm.tqdm(list(range(500))):

    positions = np.random.randint(0, height + 1, size=(2, 2))
    start = tuple(positions[0, :]) 
    goal = tuple(positions[1, :]) 

    s = time.perf_counter_ns()
    cpath = cnavigate(start, goal, walls)
    ctime.append((time.perf_counter_ns() - s))

    s = time.perf_counter_ns()
    ppath = navigate(start, goal, walls)
    ptime.append((time.perf_counter_ns() - s))

    cpath = np.array(cpath)
    ppath = np.array(ppath)

    if np.any(cpath != ppath):
        print(cpath)
        print(ppath)
        raise ValueError("Not equal")
    

ptime = np.array(ptime)
print("ptime", np.mean(ptime / (10 ** 6)))

ctime = np.array(ctime)
print("ctime", np.mean(ctime / (10 ** 6)))