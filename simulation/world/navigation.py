import numpy as np
import heapq
import time

from .grid import Grid
from .poi import PointsOfInterests
from ..state import State


pi = np.pi
state = State()

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
        self.paths = [None for _ in range(state.agent_position.shape[0])]

    

    def heuristic(self, source, destination):
        return abs(source[0] - destination[0]) + abs(source[1] - destination[1]) + self.grid.density[source[0], source[1]]
    
    def point(self, i_agent: int) -> bool:

        agent_coords: np.ndarray = state.agent_coords[i_agent, :] 
        path = self.paths[i_agent]
        nex_step = path[0, :]

        goal_coord = path[-1, :]
        agent_pos = state.agent_position[i_agent, :]

        if np.max(np.abs(agent_coords - goal_coord)) <= 1:
            self.paths[i_agent] = None
            return True

        if np.allclose(agent_coords, nex_step):
            self.paths[i_agent] = path[1:, :]
            nex_step = path[1, :]

        cell_pos = self.grid.cell_pos_to_world_pos(nex_step, 1)
        delta = cell_pos - agent_pos
        #delta = np.clip(np.round(delta), -1, 1)
        #angle = self.delta_to_angle[tuple(delta.astype(int))]

        # TODO WHY + (PI / 2) : ((((
        # angle = np.arctan2(-delta[1], delta[0]) + (pi / 2)
        angle = np.arctan2(delta[1], delta[0])
        state.agent_angle[i_agent] = angle

        return False
        
    def navigate_agent(self, i_agent: int):
        agent_coords = state.agent_coords[i_agent]
        rand_poi_i = np.random.choice(self.pois.coords.shape[0])
        new_path = self.navigate(tuple(agent_coords), tuple(self.pois.coords[rand_poi_i]))
        self.paths[i_agent] = new_path

    def tick(self):
        return
        agents_coords = self.grid.vectorized_world_to_cell(state.agent_position)
        for i_agent, path in enumerate(self.paths):

            if path is not None:
                self.point(i_agent, agents_coords[i_agent])
                continue
            
            rand_poi_i = np.random.choice(self.pois.coords.shape[0])
            new_path = self.navigate(tuple(agents_coords[i_agent, :]), tuple(self.pois.coords[rand_poi_i]))
            self.paths[i_agent] = new_path
        

    def navigate(self, start: tuple[int, int], goal: tuple[int, int]) -> list:
        """Perform the A* algorithm with a given grid, start and goal positions."""
        walls = self.grid.walls
        
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
                return np.array(path)
            
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
                        f_score = tentative_g_score + self.heuristic(neighbor, goal)
                        heapq.heappush(open_set, (f_score, neighbor))
        
        return None  # No path found