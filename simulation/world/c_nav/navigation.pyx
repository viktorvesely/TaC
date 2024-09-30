from heapq import heappush, heappop

cdef inline int heuristic(tuple source, tuple destination):
    cdef int dx = source[0] - destination[0]
    cdef int dy = source[1] - destination[1]
    return abs(dx) + abs(dy)

cpdef list navigate(tuple start, tuple goal, const double[:, :] walls):
    """
    Perform the A* algorithm with a given grid, start and goal positions.
    """
    cdef int nrows = walls.shape[0]
    cdef int ncols = walls.shape[1]

    # Priority queue: stores tuples (cost, position)
    cdef list open_set = []
    heappush(open_set, (heuristic(start, goal), start))

    # Came from: to reconstruct the path
    cdef dict came_from = {}

    # Cost from start to a node
    cdef dict g_score = {}
    g_score[start] = 0

    # Set of visited nodes
    cdef set closed_set = set()

    cdef int current_cost
    cdef tuple current
    cdef tuple neighbor
    cdef int nx, ny
    cdef int tentative_g_score
    cdef int f_score
    cdef double wall_value
    cdef list path
    cdef int dx, dy


    while open_set:
        current_cost, current = heappop(open_set)

        if current == goal:
            # Reconstruct path
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            path.reverse()
            return path

        closed_set.add(current)

        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if (dx == 0) and (dy == 0):
                    continue

                nx = current[0] + dx
                ny = current[1] + dy
                neighbor = (current[0] + dx, current[1] + dy)

                # Check if within bounds
                if 0 <= nx < nrows and 0 <= ny < ncols:
                    wall_value = walls[nx, ny]
                    # Check if passable
                    if (wall_value > 0.0) and (neighbor != goal):
                        continue

                    if neighbor in closed_set:
                        continue

                    tentative_g_score = g_score[current] + 1

                    if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                        # This path to neighbor is better than any previous one. Record it!
                        came_from[neighbor] = current
                        g_score[neighbor] = tentative_g_score
                        f_score = tentative_g_score + heuristic(neighbor, goal)
                        heappush(open_set, (f_score, neighbor))

    return None  # No path found