import numpy as np
import random
from ...state import State

state = State()

class CitizenActions:
    @staticmethod
    def select_action(i_agent: int):
        if state.agent_near_poi[i_agent]:
            return random.choices(
                [CitizenActions.stop_at_poi, CitizenActions.look_at_poi, CitizenActions.move_away],
                weights=[0.3, 0.4, 0.3]  # 30% of stopping at poi, 40% of stopping and looking at poi, 30% of moving away
            )[0](i_agent)  # Call the selected action
        else:
            return random.choices(
                [CitizenActions.start_roaming, CitizenActions.move_to_poi],
                weights=[0.5, 0.5]  # 50% of roaming randomly, 40% move at POI, 10% engage in social interaction
            )[0](i_agent)  # Call the selected action

    @staticmethod
    def start_roaming(i_agent: int):
        return CitizenActions.roaming()
    
    @staticmethod
    def roaming():

        finish_t = state.t + np.random.normal(loc=10_000, scale=1_000)
        multiplier = random.choice([-1, 1])

        def action(i_agent: int):
            
            if state.t >= finish_t:
                return CitizenActions.select_action
            
            state.world.agents.look_random(i_agent, multiplier)
            
            return action
        
        return action

    @staticmethod
    def move_to_poi(i_agent: int):
        # Get the target POI position

        # CALL TO NAVIGATION HANDLES MOVEMENT BY DEFAULT
        target_poi_index = state.world.maps.get_target_poi_index(i_agent)
        last_poi_index = state.last_poi_visited[i_agent]

        while target_poi_index == last_poi_index:
            target_poi_index = state.world.maps.get_target_poi_index(i_agent)
        
        target_poi_position = state.world.maps.get_poi_position(target_poi_index)  # Method to get position of selected POI
        
        distance_to_poi = np.linalg.norm(state.agent_position[i_agent] - target_poi_position)
        # WIPWIPWIP
        # If the agent is near the POI, handle arrival
        if distance_to_poi < 8:  # Treshold for being at the point
            state.agent_near_poi[i_agent] = True  # Set the flag to true when near the POI
            state.last_poi_visited[i_agent] = target_poi_index
            return CitizenActions.stop_at_poi(i_agent)  # Go stop at POI

        # Probably already implemented
        direction = (target_poi_position - state.agent_position[i_agent]) / distance_to_poi  # Normalize the direction vector
        state.agent_velocity[i_agent] = direction * state.agent_speed[i_agent]  # Update the velocity based on speed

        # Probably already implemented
        state.agent_position[i_agent] += state.agent_velocity[i_agent] * state.dTick

        return CitizenActions.move_to_poi  # Keep the agent in this action


    @staticmethod
    def stop_at_poi(i_agent: int):
        # Define how long the agent will stop at the POI
        stop_duration = np.random.normal(loc=5, scale=1)  # Stop for random time
        finish_time = state.t + stop_duration
        
        # Get the attraction factor of the POI (defined between 0 and 1)
        attraction_factor = state.world.pois.get_poi_attraction_factor(i_agent)

        if np.random.rand() < attraction_factor: # decide whether to look at POI or not
            poi_position = state.world.maps.get_poi_position(i_agent)
            direction_to_poi = poi_position - state.agent_position[i_agent]
            state.agent_angle[i_agent] = np.arctan2(direction_to_poi[1], direction_to_poi[0])
        else: # Look in random direction
            state.agent_angle[i_agent] = np.random.uniform(0, 2 * np.pi)
        
        def action(i_agent: int): 
            # Continue stopping until the stop duration is reached
            if state.t >= finish_time:
                return CitizenActions.move_away  # Move away from POI
            
            return action  # Keep stopping at the POI

    @staticmethod
    def social_interaction(i_agent: int):
        engagement_probability = 0.5  # Define the probability of engaging in social interaction
        # Get the positions of all citizens within a range defined as "nearby"
        nearby_agents = state.world.get_nearby_citizens(i_agent)  # Implement this
        for target_agent in nearby_agents:
            if np.random.rand() < engagement_probability:  # Define engagement_probability
                # Both citizens agree to interact
                return CitizenActions.stop_at_citizen(i_agent, target_agent)  # You may want to adjust this to reflect a stopping interaction

    @staticmethod
    def stop_at_citizen(i_agent: int, target_agent: int):
        # Determine the positions of both citizens
        target_position = state.agent_position[target_agent]
        current_position = state.agent_position[i_agent]
        
        # Calculate the direction towards the target agent
        direction = target_position - current_position
        distance = np.linalg.norm(direction)
        
        # Normalize the direction if distance is greater than a threshold
        if distance > 8:  # Define this threshold
            direction_normalized = direction / distance
            state.agent_velocity[i_agent] = direction_normalized * state.agent_speed[i_agent]
            state.agent_position[i_agent] += state.agent_velocity[i_agent] * state.dTick

            # You can similarly move the target agent towards the interacting agent if desired
            state.agent_velocity[target_agent] = -direction_normalized * state.agent_speed[target_agent]
            state.agent_position[target_agent] += state.agent_velocity[target_agent] * state.dTick
            
            return CitizenActions.stop_at_citizen(i_agent, target_agent)  # Keep moving until close enough

        # If they're close enough, initiate interaction
        interaction_duration = np.random.uniform(5000, 15000)
        finish_time = state.t + interaction_duration

        # Set both agents' angles to look at each other
        direction_to_target = target_position - current_position
        state.agent_angle[i_agent] = np.arctan2(direction_to_target[1], direction_to_target[0])
        
        direction_to_citizen = current_position - target_position
        state.agent_angle[target_agent] = np.arctan2(direction_to_citizen[1], direction_to_citizen[0])

        # Logic for stopping and engaging
        while state.t < finish_time:
            state.agent_velocity[i_agent] = 0
            state.agent_velocity[target_agent] = 0
        
        # After the interaction, both citizens will move away
        CitizenActions.move_away(i_agent)
        CitizenActions.move_away(target_agent)
        return


    @staticmethod
    def move_away(i_agent: int):
        state.agent_near_poi[i_agent] = False   # Set flag false
        return CitizenActions.start_roaming[i_agent] # Select another action