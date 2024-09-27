import numpy as np
from navigation import astar

# Create a sample grid
height, width = 100, 100
walls = np.zeros((height, width), dtype=np.double)

# Add some obstacles
walls[50, :] = 1.0
walls[:, 50] = 1.0

# Define start and goal positions
from_i, from_j = 0, 0
to_i, to_j = 99, 99

# Find the path
print("dwadw")
path = astar(from_i, from_j, to_i, to_j, walls)
print("kek")
print(type(path))
print("Path length:", len(path))
