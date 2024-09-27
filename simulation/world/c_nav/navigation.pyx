# cython: boundscheck=False, wraparound=False, cdivision=True
import numpy as np
cimport numpy as np
from libc.math cimport sqrt
from libc.stdlib cimport malloc, free
from cython cimport boundscheck, wraparound, cdivision, nonecheck
from cython.operator cimport dereference
cimport numpy as cnp
cnp.import_array()

cdef double heuristic(int x1, int y1, int x2, int y2) noexcept nogil:
    cdef double dx = abs(x1 - x2)
    cdef double dy = abs(y1 - y2)
    return (dx + dy) + (sqrt(2.0) - 2) * min(dx, dy)

cdef struct HeapItem:
    double f_score
    int i
    int j

cdef void heap_push(HeapItem* heap, int* heap_size_ptr, HeapItem item) noexcept nogil:
    cdef int i = dereference(heap_size_ptr)
    cdef int parent
    heap[i] = item
    while i > 0:
        parent = (i - 1) >> 1
        if heap[parent].f_score <= heap[i].f_score:
            break
        # Swap
        heap[i], heap[parent] = heap[parent], heap[i]
        i = parent
    heap_size_ptr[0] += 1

cdef HeapItem heap_pop(HeapItem* heap, int* heap_size_ptr) noexcept nogil:
    cdef int i = 0
    cdef int left, right, smallest
    cdef int size = dereference(heap_size_ptr) - 1
    cdef HeapItem item = heap[0]
    heap[0] = heap[size]
    heap_size_ptr[0] -= 1
    while True:
        left = (i << 1) + 1
        right = (i << 1) + 2
        smallest = i
        if left < dereference(heap_size_ptr) and heap[left].f_score < heap[smallest].f_score:
            smallest = left
        if right < dereference(heap_size_ptr) and heap[right].f_score < heap[smallest].f_score:
            smallest = right
        if smallest == i:
            break
        # Swap
        heap[i], heap[smallest] = heap[smallest], heap[i]
        i = smallest
    return item


# @boundscheck(False)
# @wraparound(False)
# @cdivision(True)
def astar(int from_i, int from_j, int to_i, int to_j, double[:, :] walls):
    """
    Perform the A* algorithm to find the shortest path from (from_i, from_j)
    to (to_i, to_j) in a grid where walls[i,j] > 0.0 are obstacles.

    Parameters:
    - from_i, from_j: Starting coordinates.
    - to_i, to_j: Destination coordinates.
    - walls: 2D array where values > 0.0 represent impassable objects.

    Returns:
    - List of (i, j) tuples representing the path from start to goal.
    """
    cdef int height = walls.shape[0]
    cdef int width = walls.shape[1]
    cdef double[:, :] g_score = np.full((height, width), np.inf, dtype=np.double)
    cdef double[:, :] f_score = np.full((height, width), np.inf, dtype=np.double)
    cdef int[:, :] came_from_i = np.full((height, width), -1, dtype=np.intc)
    cdef int[:, :] came_from_j = np.full((height, width), -1, dtype=np.intc)

    cdef double SQRT2 = sqrt(2.0)
    cdef cnp.ndarray[cnp.int32_t, ndim=2] offsets_array = np.zeros((8, 2), dtype=np.int32)
    cdef int[:, :] offsets = offsets_array
    offsets[0][0], offsets[0][1] = -1, -1  # Up-Left
    offsets[1][0], offsets[1][1] = -1,  0  # Up
    offsets[2][0], offsets[2][1] = -1,  1  # Up-Right
    offsets[3][0], offsets[3][1] =  0, -1  # Left
    offsets[4][0], offsets[4][1] =  0,  1  # Right
    offsets[5][0], offsets[5][1] =  1, -1  # Down-Left
    offsets[6][0], offsets[6][1] =  1,  0  # Down
    offsets[7][0], offsets[7][1] =  1,  1  # Down-Right


    cdef int max_heap_size = height * width
    cdef int heap_size = 0
    cdef HeapItem* heap = <HeapItem*> malloc(max_heap_size * sizeof(HeapItem))
    if heap == NULL:
        raise MemoryError("Unable to allocate memory for the heap.")

    g_score[from_i, from_j] = 0.0
    f_score[from_i, from_j] = heuristic(from_i, from_j, to_i, to_j)

    cdef HeapItem start_item
    start_item.f_score = f_score[from_i, from_j]
    start_item.i = from_i
    start_item.j = from_j
    heap_push(heap, &heap_size, start_item)

    cdef int current_i, current_j, neighbor_i, neighbor_j, k
    cdef double tentative_g_score, move_cost
    cdef HeapItem current_item, neighbor_item


    while heap_size > 0:
        current_item = heap_pop(heap, &heap_size)
        current_i = current_item.i
        current_j = current_item.j

        if current_i == to_i and current_j == to_j:
            break  # Path found

        for k in range(8):
            neighbor_i = current_i + offsets[k][0]
            neighbor_j = current_j + offsets[k][1]

            if 0 <= neighbor_i < height and 0 <= neighbor_j < width:
                if walls[neighbor_i, neighbor_j] > 0.0:
                    continue

                if offsets[k][0] == 0 or offsets[k][1] == 0:
                    move_cost = 1.0
                else:
                    move_cost = SQRT2

                tentative_g_score = g_score[current_i, current_j] + move_cost

                if tentative_g_score < g_score[neighbor_i, neighbor_j]:
                    came_from_i[neighbor_i, neighbor_j] = current_i
                    came_from_j[neighbor_i, neighbor_j] = current_j
                    g_score[neighbor_i, neighbor_j] = tentative_g_score
                    f_score[neighbor_i, neighbor_j] = tentative_g_score + heuristic(
                        neighbor_i, neighbor_j, to_i, to_j
                    )

                    neighbor_item.f_score = f_score[neighbor_i, neighbor_j]
                    neighbor_item.i = neighbor_i
                    neighbor_item.j = neighbor_j
                    heap_push(heap, &heap_size, neighbor_item)

    free(heap)

    return reconstruct_path(came_from_i, came_from_j, from_i, from_j, to_i, to_j)

def reconstruct_path(int[:, :] came_from_i, int[:, :] came_from_j,
                     int from_i, int from_j, int to_i, int to_j):
    """
    Reconstructs the path from the came_from arrays.

    Returns:
    - List of (i, j) tuples representing the path from start to goal.
    """
    cdef list path = []
    cdef int current_i = to_i
    cdef int current_j = to_j
    cdef int temp_i, temp_j

    while current_i != from_i or current_j != from_j:
        path.append((current_i, current_j))
        temp_i = came_from_i[current_i, current_j]
        temp_j = came_from_j[current_i, current_j]
        current_i, current_j = temp_i, temp_j
    path.append((from_i, from_j))
    path.reverse()
    return path
