import numpy as np
cimport numpy as cnp
from libc.math cimport sin, cos
from libc.stdio cimport printf
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

cdef inline void cast_ray_filling(
    double ray_angle,
    double step_size,
    int n_steps,
    double x_origin,
    double y_origin,
    int i_agent,
    double[:, :] walls,
    int[:, :] density,
    int[:, :] offsets,
    int[:] agent_indicies,
    int[:] agents_in_vision,
    int* current_agents_in_vision,
    int max_agents_in_vision,
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
    cdef Coords coords, last_coords
    last_coords.i = -150
    last_coords.j = -237
    cdef int i_step
    cdef double vision_strength = 0.4;
    cdef double vision_falloff = (vision_strength - 0.1) / (<double>n_steps)
    cdef double vision_reduction
    cdef double wall_value
    cdef int density_value, offset
    cdef int i, target_i


    # Skip first step due to it being in the same spot for all rays
    for i_step in range(1, n_steps + 1):

        position[0] = x_origin + delta[0] * (<double>i_step)
        position[1] = y_origin + delta[1] * (<double>i_step)

        coords = world_to_cell(position, world_TL, grid_size, i_tot, j_tot)

        if (coords.i == -1) or (coords.j == -1):
            break

        if (last_coords.i == coords.i) and (last_coords.j == coords.j):
            continue

        last_coords.i = coords.i
        last_coords.j = coords.j

        # Wall vision reduction
        wall_value = walls[coords.i, coords.j]
        if wall_value >= 0.999:
            break

        vision_reduction = 1.0 - wall_value
        vision_strength *= vision_reduction

        # Density vision reduction
        # TODO no self density intersection
        density_value = density[coords.i, coords.j]
        # vision_reduction = 0.37 / ((<double>density_value) + 0.37) 
        # vision_strength *= vision_reduction

        if wall_value == 0.0:
            vision_field[coords.i, coords.j] += vision_strength

        # Check for agents in vision
        if (density_value > 0) and ((current_agents_in_vision[0]) < max_agents_in_vision):
            offset = offsets[coords.i, coords.j]
            for i in range(density_value):
                
                if current_agents_in_vision[0] >= max_agents_in_vision:
                    break

                target_i = agent_indicies[offset + i]

                if target_i == i_agent:
                    continue
                
                if random() > vision_strength:
                    continue

                # TODO target_i can be added twice (when two rays intersect the same cell)
                agents_in_vision[current_agents_in_vision[0]] = target_i
                current_agents_in_vision[0] += 1
        

        # Apply vision falloff
        vision_strength -= vision_falloff
        vision_strength = max(0.0, vision_strength)
        
        

        
cdef void _generate_vision_field(
    double[:, :] agent_position,
    double[:] agent_angles,
    double[:, :] walls,
    int[:, :] density,
    int[:, :] offsets,
    int[:] agent_indicies,
    int[:, :] agents_in_vision,
    int[:] current_agents_in_vision,
    int max_agents_in_vision,
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
    cdef double ray_angle, diverger
    cdef double agent_x, agent_y

    cdef int i_agent, i_ray

    for i_agent in prange(n_agents, nogil=True):
        
        agent_x = agent_position[i_agent, 0]
        agent_y = agent_position[i_agent, 1]
        agent_angle = agent_angles[i_agent]

        for i_ray in range(n_rays):

            if i_ray % 2 == 0:
                diverger = -(<double>(i_ray)) / 2
            else:
                diverger = (<double>i_ray)

            ray_angle = agent_angle + fov_step * diverger
            
            cast_ray_filling(
                ray_angle,
                step_size,
                n_steps,
                agent_x,
                agent_y,
                i_agent,
                walls,
                density,
                offsets,
                agent_indicies,
                agents_in_vision[i_agent, :],
                &current_agents_in_vision[i_agent],
                max_agents_in_vision,
                vision_field,
                world_TL,
                grid_size,
                i_tot,
                j_tot
            )

def generate_vision_field(
    double[:, :] agent_position not None,
    double[:] agent_angles not None,
    double[:, :] walls not None,
    int[:, :] density not None,
    int[:, :] offsets not None,
    int[:] agent_indicies not None,
    int[:, :] agents_in_vision not None,
    double[:] world_TL,
    double grid_size,
    double vision_length,
    double fov,
    int n_rays,
    ):

    cdef int i_tot = walls.shape[0]
    cdef int j_tot = walls.shape[1]
    cdef int n_agents = agent_position.shape[0]
    cdef int max_agents_in_vision = agents_in_vision.shape[1]
    vision_field_array = np.zeros((i_tot, j_tot), dtype=np.float64)
    cdef double[:, :] vision_field = vision_field_array
    
    current_agents_in_vision = np.zeros((n_agents,), dtype=np.int32)

    _generate_vision_field(
        agent_position,
        agent_angles,
        walls,
        density,
        offsets,
        agent_indicies,
        agents_in_vision,
        current_agents_in_vision,
        max_agents_in_vision,
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
