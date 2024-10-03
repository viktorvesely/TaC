import random
import numpy as np
from ...state import State
from ...events.event import TheftEvent, TheftAborted, ChosenTargetEvent

class ThiefActions():
    """
    Contains the actions of the thief agent.
    """

    @staticmethod
    def select_almost_empty_area(i_agent: int, state: State):

        walkable_density = state.grid.blurry_density[state.grid.walkable_mask].flatten().astype(float)
        weights = 12 * np.exp(-np.power(walkable_density - 1.69, 2) / 2) + 0.1
        weights = weights / weights.sum()
        walkable_inds = state.grid.grid_indicies[state.grid.walkable_mask].flatten()

        go_to = np.random.choice(walkable_inds, p=weights)
        
        # Yuo can create your own heuristic function
        state.world.maps.navigate_agent(i_agent, go_to, heuristic=None)
        return ThiefActions.navigate(i_agent, state)
    
    @staticmethod
    def navigate(i_agent: int, state: State):

        target_look_period = 1_000
        next_target_look = state.t

        def action(i_agent: int, state: State):
            nonlocal next_target_look
            # Check if the agent has reached the point of interest

            search_for_target = state.t >= next_target_look

            if state.world.maps.execute_path(i_agent):
                # If the point of interest is reached, select the next point of interest
                return ThiefActions.select_almost_empty_area
            elif (state.agent_motivations[i_agent] >= 0.5) and search_for_target:
                next_target_look = state.t + target_look_period

                target = ThiefActions.look_for_target(i_agent, state)

                if target != -1:
                    state.maps.paths[i_agent] = None
                    return ThiefActions.approach_target(i_agent, target, state)
            # Continue navigating until the point of interest is reached
            return action
        
        return action
    
    @staticmethod
    def look_for_target(i_agent: int, state: State):
        """
        If an appropriate target is found, start approaching.
        Otherwise, continue looking for a target.
        """
        agents_in_vision = state.agents_in_vision[i_agent, :]
        agent_mask = agents_in_vision != -1
        agent_in_vision_inds = agents_in_vision[agent_mask]
        motivation = state.agent_motivations[i_agent, 0]
        
        # Check if there are any visible agents
        closest_target = -1
        closest_target_dist = float("inf")
        closest_p_not_caught = -1
        for target_i in agent_in_vision_inds:

            if not state.agent_is_citizen[target_i]:
                continue

            target_pos = state.agent_coords[target_i]
            from_thief_to_target = target_pos - state.agent_position[i_agent]

            #normalize distance
            distance = np.linalg.norm(from_thief_to_target)
            from_thief_to_target = from_thief_to_target / distance
            approach_cos_angle = np.dot(from_thief_to_target, state.agent_heading_vec[target_i])
            p_not_caught_by_target = approach_cos_angle / 2 + 0.5
            p_not_caught_by_target = max(p_not_caught_by_target, 0.03)

            threshold = p_not_caught_by_target * motivation

            if (random.random() < threshold) and (closest_target_dist > distance):
                closest_target_dist = distance
                closest_target = target_i
                closest_p_not_caught = p_not_caught_by_target
                        
        if closest_target == -1:
            # state.agent_motivations[i_agent, 0] -= 0.05
            # state.maps.paths[i_agent] = None
            return closest_target
        
        ChosenTargetEvent(state, i_agent, closest_target, motivation, closest_target_dist, closest_p_not_caught)
        return closest_target

    @staticmethod
    def approach_target(i_agent: int, target_i: int, state: State):
        """
        Approach the target. If close enough, attempt theft.
        """
        state.agent_speed[i_agent, :] = 0.16  # Increase speed while approaching
        approach_start = state.t

        def action(i_agent: int, state: State):

            
            time_reason = (state.t - approach_start) > 3_000
            motivation = state.agent_motivations[i_agent, 0]
            motivation_reason = motivation < 0.48  
            if time_reason or motivation_reason:
                state.agent_speed[i_agent, :] = 0.1
                TheftAborted(state, i_agent, motivation, np.nan, reason=("time" if time_reason else "motivation"))
                return ThiefActions.select_almost_empty_area
        
            # TODO evaluate theft here decrease motivation if target looks at you
        
            # Calculate distance to the target
            delta = state.agent_position[i_agent, :] - state.agent_position[target_i, :]
            target_heading = state.agent_heading_vec[target_i, :]
            distance = np.linalg.norm(delta)
            cos = np.dot(delta / distance, target_heading)
            p_caught = cos / 2 + 0.5

            if (p_caught > 0.9) and (random.random() < p_caught):
                state.agent_speed[i_agent, :] = 0.1
                TheftAborted(state, i_agent, motivation, distance, reason='turned')
                return ThiefActions.select_almost_empty_area

            angle = np.arctan2(-delta[1], -delta[0])
            state.agent_angle[i_agent] = angle
            if distance < (state.vars.agent_size * 3.2):
                state.agent_speed[i_agent, :] = 0.1
                return ThiefActions.theft(i_agent, target_i, state)
            return action  # Keep approaching if not close enough
        
        return action

    @staticmethod
    def theft(i_agent: int, target_i: int, state: State):
        """
        Attempt to steal from the target.
        """

        target_pos = state.agent_position[target_i]
        from_target_to_thief = state.agent_position[i_agent] - target_pos

        from_target_to_thief = from_target_to_thief / np.linalg.norm(from_target_to_thief)
        approach_cos_angle = np.dot(from_target_to_thief, state.agent_heading_vec[target_i])
        p_caught_by_target = approach_cos_angle / 2 + 0.5
        p_caught_by_target = max(p_caught_by_target - 0.4, 0.0)

        thief_coords = state.agent_coords[i_agent, :]
        vision_value = state.world.vision.values[thief_coords[0], thief_coords[1]]
        p_caught_by_others = min(vision_value, 0.95)
        
        p_caught = max(p_caught_by_target, p_caught_by_others)
        
        caught = random.random() < p_caught
        # print(i_agent, "fail" if caught else "succ", f"{p_caught_by_target:.2f}")

        state.agent_last_rob[i_agent] = state.t
        TheftEvent(state, caught, i_agent, target_i, vision_value, approach_cos_angle)
        if caught:
            state.agent_motivations[i_agent] = 0.2
        else:
            state.agent_motivations[i_agent] = 0.2

        return ThiefActions.select_almost_empty_area
    

