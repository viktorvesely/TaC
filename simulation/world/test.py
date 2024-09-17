from vision.vision import add_matrix
import numpy as np

a = np.ones((3, 2))
b = np.ones((3, 2)) * 2

print(add_matrix(a, b))