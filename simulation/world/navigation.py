from typing import Callable
import numpy as np
import heapq
import time
import math

from .grid import Grid
from .poi import PointsOfInterests
from ..state import State


pi = np.pi
state = State()

type HeuristicFunc = Callable[[tuple[int, int], tuple[int, int]], float]

class GoogleMaps:

    delta_to_angle = {
        (-1, 0): pi / 2,
        (1, 0): -pi / 2,
        (0, 1): 0,
        (0, -1): pi,
    }

    # Directions for moving in the grid (up, down, left, right)
    neighbors = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, -1), (-1, 1), (1, 1), (-1, -1)]

    def __init__(self, grid: Grid, pois: PointsOfInterests) -> None:
        self.grid = grid
        self.pois = pois
        self.paths: list[list[tuple[int, int]] | None] = [None for _ in range(state.agent_position.shape[0])]


    def heuristic_avoid_dense(self, source: tuple[int, int], destination: tuple[int, int]) -> float:
        return abs(source[0] - destination[0]) + abs(source[1] - destination[1]) + self.grid.density[source[0], source[1]]
    
    
    def heuristic(self, source: tuple[int, int], destination: tuple[int, int]) -> float:
        return abs(source[0] - destination[0]) + abs(source[1] - destination[1])

    def execute_path(self, i_agent: int) -> bool:

        agent_coords = state.agent_coords[i_agent, :].tolist()

        path = self.paths[i_agent]
        if path is None:
            return True
        
        next_step = path[0]
        goal_coord = path[-1]

        max_delta = max(abs(agent_coords[0] - goal_coord[0]), abs(agent_coords[1] - goal_coord[1]))
        if max_delta <= 1:
            self.paths[i_agent] = None
            return True

        if (agent_coords[0] == next_step[0]) and (agent_coords[1] == next_step[1]):
            self.paths[i_agent].pop(0)
            next_step = path[0]

        #cell_pos = self.grid.cell_pos_to_world_pos(next_step, 1)
        cell_pos = (
            next_step[1] * self.grid.size + self.grid.world_TL[0] + self.grid._tomid[0],
            next_step[0] * self.grid.size + self.grid.world_TL[1] + self.grid._tomid[1]
        )

        # delta = cell_pos - agent_pos
        agent_pos = state.agent_position[i_agent, :].tolist()
        angle = math.atan2(cell_pos[1] - agent_pos[1], cell_pos[0] - agent_pos[0])
        state.agent_angle[i_agent] = angle

        return False
        
    def navigate_agent(self, i_agent: int, to: tuple[int, int], heuristic: HeuristicFunc | None = None):
        agent_coords = state.agent_coords[i_agent]
        new_path = self.navigate(tuple(agent_coords), to, heuristic)
        self.paths[i_agent] = new_path

        
    def get_target_poi_index(self, i_agent: int) -> int:
        return 0

    def get_poi_position(self, i_poi: int) -> np.ndarray:
        return self.pois.coords[i_poi]

    def navigate(
            self,
            start: tuple[int, int],
            goal: tuple[int, int],
            heuristic: HeuristicFunc | None = None

        ) -> list:
        # TODO fix navigation it is slow as hell
        """Perform the A* algorithm with a given grid, start and goal positions."""
        walls = self.grid.walls

        heuristic = heuristic if heuristic is not None else self.heuristic 
        
        # Priority queue: stores tuples (cost, position)
        open_set = []
        heapq.heappush(open_set, (0 + self.heuristic(start, goal), start))
        
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
            for dx, dy in self.neighbors:
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