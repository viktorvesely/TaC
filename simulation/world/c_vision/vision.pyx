import numpy as np
cimport numpy as cnp
from libc.math cimport sin, cos
from libc.stdio cimport printf
from cython.parallel import prange
from cython import boundscheck

cnp.import_array()

cdef struct Coords:
    int i
    int j

@boundscheck(False)
cdef Coords world_to_cell(double[2] pos, double[:] world_TL, double grid_size, int i_tot, int j_tot) noexcept nogil:
    # TODO fix out of bounds indicies
    cdef Coords coords
    coords.i = <int>((pos[1] - world_TL[1]) // grid_size)
    coords.j = <int>((pos[0] - world_TL[0]) // grid_size)

    if (coords.i < 0) or (coords.i >= i_tot):
        coords.i = -1

    if (coords.j < 0) or (coords.j >= j_tot):
        coords.j = -1

    return coords

@boundscheck(False)
cdef void cast_ray_filling(
    double ray_angle,
    double step_size,
    int n_steps,
    double x_origin,
    double y_origin,
    double[:, :] walls,
    double[:, :] density,
    double[:, :] vision_field,
    double[:] world_TL,
    double grid_size,
    int i_tot,
    int j_tot,
) noexcept nogil:


    cdef double[2] delta
    delta[0] = cos(ray_angle) * step_size
    delta[1] = sin(ray_angle) * step_size

    cdef double[2] position
    cdef Coords coords
    cdef int i_step
    cdef double vision_strength = 1.0;
    cdef double vision_falloff = (vision_strength + 0.1) / (<double>n_steps)
    cdef double vision_reduction
    cdef double wall_value
    cdef double density_value

    # Skip first step due to it being in the same spot for all rays
    for i_step in range(1, n_steps + 1):

        position[0] = x_origin + delta[0] * (<double>i_step)
        position[1] = y_origin + delta[1] * (<double>i_step)

        coords = world_to_cell(position, world_TL, grid_size, i_tot, j_tot)

        if (coords.i == -1) or (coords.j == -1):
            break

        # Wall vision reduction
        wall_value = walls[coords.i, coords.j]
        if wall_value >= 0.999:
            break

        vision_reduction = 1.0 - wall_value
        vision_strength *= vision_reduction


        # Density vision reduction
        # TODO no self density intersection
        # density_value = density[coords.i, coords.j]
        # vision_reduction = 0.37 / (density_value + 0.37) 
        # vision_strength *= vision_reduction

        if wall_value == 0.0:
            vision_field[coords.i, coords.j] += vision_strength
        
        vision_strength -= vision_falloff
        vision_strength = max(0.0, vision_strength)

        
cdef void _generate_vision_field(
    double[:, :] agent_position,
    double[:] agent_angles,
    double[:, :] walls,
    double[:, :] density,
    double[:] world_TL,
    double grid_size,
    double vision_length,
    double fov,
    int n_rays,
    double[:, :] vision_field,
    int i_tot,
    int j_tot
) noexcept nogil:
    cdef double step_size = grid_size / 2.0
    cdef int n_steps = <int> (vision_length / step_size) 
    cdef double fov_step = fov / (<double>(n_rays - 1))

    cdef int n_agents = agent_position.shape[0]
    
    cdef double agent_angle
    cdef double ray_angle
    cdef double ray_angle_start
    cdef double agent_x, agent_y

    cdef int i_agent, i_ray

    for i_agent in prange(n_agents, nogil=True):
        
        agent_x = agent_position[i_agent, 0]
        agent_y = agent_position[i_agent, 1]
        agent_angle = agent_angles[i_agent]

        ray_angle_start = agent_angle - (fov / 2.0)

        for i_ray in range(n_rays):
            ray_angle = ray_angle_start + (<double>i_ray) * fov_step
            
            cast_ray_filling(
                ray_angle, step_size, n_steps,
                agent_x, agent_y, walls, density, vision_field,
                world_TL, grid_size, i_tot, j_tot
            )

def generate_vision_field(
    double[:, :] agent_position not None,
    double[:] agent_angles not None,
    double[:, :] walls not None,
    double[:, :] density not None,
    double[:] world_TL,
    double grid_size,
    double vision_length,
    double fov,
    int n_rays,
    ):

    cdef int i_tot = walls.shape[0]
    cdef int j_tot = walls.shape[1]
    vision_field_array = np.zeros((i_tot, j_tot), dtype=np.float64)
    cdef double[:, :] vision_field = vision_field_array
    
    _generate_vision_field(
        agent_position,
        agent_angles,
        walls,
        density,
        world_TL,
        grid_size,
        vision_length,
        fov,
        n_rays,
        vision_field,
        i_tot,
        j_tot
    )

    return np.clip(vision_field_array, 0.0, 1.0)
