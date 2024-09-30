import heapq
import numpy as np

def heuristic(source: tuple[int, int], destination: tuple[int, int]) -> float:
    return abs(source[0] - destination[0]) + abs(source[1] - destination[1])

#neighbors = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, -1), (-1, 1), (1, 1), (-1, -1)]
neighbors = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

def navigate(
        start: tuple[int, int],
        goal: tuple[int, int],
        walls: np.ndarray

    ) -> list:
    # TODO fix navigation it is slow as hell
    """Perform the A* algorithm with a given grid, start and goal positions."""

    # Priority queue: stores tuples (cost, position)
    open_set = []
    heapq.heappush(open_set, (0 + heuristic(start, goal), start))
    
    # Came from: to reconstruct the path
    came_from = {}
    
    # Cost from start to a node
    g_score = {start: 0}
    
    # Set of visited nodes
    closed_set = set()
    while open_set:
        # Get the node with the lowest score from the priority queue
        current_cost, current = heapq.heappop(open_set)
        
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
        
        # Explore neighbors
        for dx, dy in neighbors:
            neighbor = (current[0] + dx, current[1] + dy)
            
            # Check if within bounds
            if 0 <= neighbor[0] < walls.shape[0] and 0 <= neighbor[1] < walls.shape[1]:
                # Check if passable
                if (walls[neighbor[0], neighbor[1]] > 0) and (neighbor != goal):
                    continue
                
                if neighbor in closed_set:
                    continue
                
                # Tentative g score
                tentative_g_score = g_score[current] + 1
                
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    # This path to neighbor is better than any previous one. Record it!
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score = tentative_g_score + heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score, neighbor))
    
    return None  # No path found