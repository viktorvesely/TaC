cimport numpy as cnp
from libc.math cimport sqrt
from cython.parallel import prange
from cython import boundscheck, wraparound
from libc.stdlib cimport rand, RAND_MAX

cnp.import_array()

cdef struct Coords:
    int i
    int j

cdef struct Position:
    double x
    double y

@wraparound(False)
@boundscheck(False)
cdef inline Coords world_to_cell(double[2] pos, double[:] world_TL, double grid_size, int i_tot, int j_tot) noexcept nogil:
    cdef Coords coords
    coords.i = <int>((pos[1] - world_TL[1]) // grid_size)
    coords.j = <int>((pos[0] - world_TL[0]) // grid_size)

    if (coords.i < 0) or (coords.i >= i_tot):
        coords.i = -1

    if (coords.j < 0) or (coords.j >= j_tot):
        coords.j = -1

    return coords


@wraparound(False)
@boundscheck(False)
cdef inline Position cell_to_world(Coords coords, double[:] world_TL, double grid_size, int i_tot, int j_tot) noexcept nogil:
    cdef Position position
    position.x = (<double>coords.j) * grid_size + world_TL[0]
    position.x = (<double>coords.i) * grid_size + world_TL[1]
    return position
        
cdef inline double random() noexcept nogil:
    # TODO srand
    return (<double>rand()) / (<double>RAND_MAX)

    
    
cdef void _resolve_collision(
    double[:, :] agent_position,
    double[:, :] agent_velocity,
    double[:] world_TL,
    int[:, :] density,
    int[:, :] offsets,
    int[:] agent_indicies,
    double grid_size,
    int n_agents,
    int i_tot,
    int j_tot,
    double agent_size
) noexcept nogil:
    
    cdef int i_agent, target_i
    cdef int di, dj, i
    cdef double distance, remain
    cdef Coords me, other
    cdef double deltax, deltay 
    cdef double[2] mepos;
    cdef int offset, density_value

    with nogil:
        for i_agent in range(n_agents):

            mepos[0] = agent_position[i_agent, 0]
            mepos[1] = agent_position[i_agent, 1]

            me = world_to_cell(mepos, world_TL, grid_size, i_tot, j_tot)

            for di in range(-1, 2):
                for dj in range(-1, 2):
                    
                    other = Coords(me.i + di, me.j + dj)

                    if (other.i < 0) or (other.i >= i_tot) or (other.j < 0) or (other.j >= j_tot):
                        continue

                    offset = offsets[other.i, other.j]
                    density_value = density[other.i, other.j]
                    for i in range(density_value):
                
                        target_i = agent_indicies[offset + i]
                    
                        if target_i == i_agent:
                            continue

                        deltax = agent_position[i_agent, 0] - agent_position[target_i, 0];
                        deltay = agent_position[i_agent, 1] - agent_position[target_i, 1];

                        distance = sqrt(deltax * deltax + deltay * deltay)
            
                        if distance > (2 * agent_size):
                            continue

                        if distance == 0:
                            distance = 1
                            deltax = 1
                            deltay = 0

                        remain = distance - (agent_size)

                        deltax = (deltax / distance) * 0.01
                        deltay = (deltay / distance) * 0.01

                        agent_velocity[i_agent, 0] += deltax
                        agent_velocity[i_agent, 1] += deltay

                        agent_velocity[target_i, 0] -= deltax
                        agent_velocity[target_i, 1] -= deltay


def resolve_collision(
    double[:, :] agent_position,
    double[:, :] agent_velocity,
    double[:] world_TL,
    int[:, :] density,
    int[:, :] offsets,
    int[:] agent_indicies,
    double grid_size,
    int i_tot,
    int j_tot,
    double agent_size
    ):

    cdef int n_agents = agent_position.shape[0]

    _resolve_collision(
        agent_position,
        agent_velocity,
        world_TL,
        density,
        offsets,
        agent_indicies,
        grid_size,
        n_agents,
        i_tot,
        j_tot,
        agent_size
    )

