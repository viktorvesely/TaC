import numpy as np

DOWN = 0
RIGHT = 1
UP = 2
LEFT = 3

vline = 0
hline = 1
cornerBR = 2
cornerBL = 3
cornerTL = 4
cornerTR = 5
empty = 6
cross = 7
one = 8

n_grids_per_side = 3

sides = [
    (UP, (1, 0)),
    (DOWN, (-1, 0)),
    (RIGHT, (0, 1)),
    (LEFT, (0, -1)),
]

rules = [
    { # vline
        UP: {empty, vline, cornerBR, cornerBL, one, cross},
        DOWN: {empty, vline, cornerTL, cornerTR, one, cross},
        LEFT: {empty, cornerBL, cornerTL, one, cross},
        RIGHT: {empty, cornerBR, cornerTR, one, cross},
    },
    { # hline
        LEFT: {empty, hline, cornerTR, cornerBR, one, cross},
        RIGHT: {empty, hline, cornerTL, cornerBL, one, cross},
        DOWN: {empty, cornerBL, cornerBR, one, cross},
        UP: {empty, cornerTR, cornerTL, one, cross},
    }, 
    { # cornerBR
        UP: {empty, cross, one, hline, cornerTL, cornerTR},
        LEFT: {empty, cross, one, vline, cornerTL, cornerBL},
        RIGHT: {cornerTL, cornerBL, hline},
        DOWN: {cornerTL, cornerTR, vline}
    },
    { # cornerBL
        UP: {empty, cross, one, hline, cornerTL, cornerTR},
        RIGHT: {empty, cross, one, vline, cornerTR, cornerBR},
        LEFT: {cornerTR, cornerBR, hline},
        DOWN: {cornerTL, cornerTR, vline}
    },
    { # cornerTL
        DOWN: {empty, cross, one, hline, cornerBL, cornerBR},
        RIGHT: {empty, cross, one, vline, cornerTR, cornerBR},
        LEFT: {cornerTR, cornerBR, hline},
        UP: {cornerBR, cornerBL, vline}
    },
    { # cornerTR
        DOWN: {empty, cross, one, hline, cornerBR, cornerBL},
        LEFT: {empty, cross, one, vline, cornerTL, cornerBL},
        RIGHT: {cornerTL, cornerBL, hline},
        UP: {cornerBR, cornerBL, vline}
    },
    { # empty
        DOWN: {empty, cross, one, vline, hline, cornerBR, cornerBL},
        UP: {empty, cross, one, vline, hline, cornerTR, cornerTL},
        LEFT: {empty, cross, one, vline, hline, cornerTL, cornerBL},
        RIGHT: {empty, cross, one, vline, hline, cornerTR, cornerBR},
    },
    { # full
        DOWN: {empty, cross, one, vline, hline},
        UP: {empty, cross, one, vline, hline},
        LEFT: {empty, cross, one, hline, vline},
        RIGHT: {empty, cross, one, hline, vline},
    },
    { # one
        DOWN: {empty, cross, vline, hline},
        UP: {empty, cross, vline, hline},
        LEFT: {empty, cross, hline, vline},
        RIGHT: {empty, cross, hline, vline},
    },
]

types_to_array = [
    np.array([
        [0, 1, 0],
        [0, 1, 0],
        [0, 1, 0]
    ]),
    np.array([
        [0, 0, 0],
        [1, 1, 1],
        [0, 0, 0]
    ]),
    np.array([
        [0, 0, 0],
        [0, 1, 1],
        [0, 1, 0]
    ]),
    np.array([
        [0, 0, 0],
        [1, 1, 0],
        [0, 1, 0]
    ]),
    np.array([
        [0, 1, 0],
        [1, 1, 0],
        [0, 0, 0]
    ]),
    np.array([
        [0, 1, 0],
        [0, 1, 1],
        [0, 0, 0]
    ]),
    np.array([
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0]
    ]),
    np.array([
        [0, 1, 0],
        [1, 1, 1],
        [0, 1, 0]
    ]),
    np.array([
        [0, 0, 0],
        [0, 1, 0],
        [0, 0, 0]
    ]),
]

w_objects = np.array([
    30, # vline
    30, # hline
    10, # corners
    10,
    10,
    10,
    10, # empty
    10, # cross
    8 # one
])

class WorldGenerator:

    n_grids_per_side: int = 3

    def __init__(self, n_grids: int):

        if (n_grids % self.n_grids_per_side) != 0:
            raise ValueError(f"n_grids needs to be divisible by {self.n_grids_per_side}")

        self.n_grids = n_grids
        self.N = int(n_grids / self.n_grids_per_side)
        self.wave = np.full((self.N, self.N, len(rules)), True, dtype=bool)

    def update_neighbours(self, io: int, jo: int, world: np.ndarray):

        q = []

        for DIR_TO, (di, dj) in sides:
            ni = io + di
            nj = jo + dj
            q.append((DIR_TO, (ni, nj), (io, jo)))
        
        while len(q) > 0:
            
            DIR_TO_ME, (i, j), (pi, pj) = q.pop(0)

            if (
                (i < 0) or
                (i >= self.N) or
                (j < 0) or
                (j >= self.N)
            ):
                continue

            if world[i, j] != -1:
                continue

            previous_possible_objects = np.where(self.wave[pi, pj])[0]
            if len(previous_possible_objects) == 0:
                previous_possible_objects = [world[pi, pj]]

            possible_objects = np.where(self.wave[i, j])[0]
            set_possible_objects = set(possible_objects)
            n_possible = len(set_possible_objects)
            allowed_objects = set()

            for i_prev_object in previous_possible_objects:
                allowed_objects |= rules[i_prev_object][DIR_TO_ME]

            set_possible_objects = set_possible_objects.intersection(allowed_objects)

            if n_possible <= len(set_possible_objects):
                continue

            self.wave[i, j, :] = False
            for possible_i in set_possible_objects:
                self.wave[i, j, possible_i] = True

            for DIR_TO, (di, dj) in sides:
                ni = i + di
                nj = j + dj
                q.append((DIR_TO, (ni, nj), (i, j)))

    def world_to_walls(self, world: np.ndarray) -> np.ndarray:
        walls = np.zeros((self.n_grids, self.n_grids))
        k = self.n_grids_per_side

        for i in range(self.N):
            for j in range(self.N):
                wi = i * k
                wj = j * k
                walls[wi:(wi+k), wj:(wj+k)] = types_to_array[world[i, j]]

        return walls

    def generate_walls(self):
        world = self.collapse_wave()
        return self.world_to_walls(world)


    def collapse_wave(self) -> np.ndarray:

        N = self.N
        wave = self.wave

        world = np.full((N, N), -1, dtype=int)

        while True:

            entropy = np.sum(wave, axis=2, dtype=float)
            collapse_mask = entropy > 0
            entropy[~collapse_mask] = np.inf

            if not np.any(collapse_mask):
                break

            # Choose next tile
            min_ent = np.min(entropy)
            inds = np.where(entropy == min_ent)
            tile_choice = np.random.randint(0, inds[0].size)
            c_i, c_j = inds[0][tile_choice], inds[1][tile_choice]

            # Choose the tile type
            possible_colapse = np.where(wave[c_i, c_j])[0]
            weights = w_objects[wave[c_i, c_j]]
            p = weights / weights.sum()
            collapse_choice = np.random.choice(possible_colapse, p=p)
            world[c_i, c_j] = collapse_choice
            wave[c_i, c_j, :] = False

            # Update neighbours
            self.update_neighbours(c_i, c_j, world)

        return world
