import numpy as np
import random
from ...state import State

state = State()

class CitizenActions:
    
    weigths = np.array([4, 4, 0])
    weigths = weigths / weigths.sum()
    
    @staticmethod
    def select_action(i_agent: int):
        return np.random.choice(
            [CitizenActions.start_roaming, CitizenActions.select_poi, CitizenActions.social_interaction],
            p=CitizenActions.weigths  # 50% of roaming randomly, 40% move at POI, 10% engage in social interaction
        )

    @staticmethod
    def start_roaming(i_agent: int):
        print("Citizen-Roaming")
        return CitizenActions.roaming()
    
    @staticmethod
    def select_poi(i_agent: int):
        print("Citizen-Selecting POI")
        state.world.maps.navigate_agent(i_agent)
        return CitizenActions.navigate
    
    @staticmethod
    def navigate(i_agent: int):
        if state.world.maps.point(i_agent):
            return CitizenActions.select_action
        return CitizenActions.navigate
    
    @staticmethod 
    def roaming(i_agent: int): 
        #Pending randomization
        finish_t = state.t + np.random.normal(loc=10_000, scale=1_000)
        multiplier = random.choice([-1, 1])

        def action(i_agent: int):
            if state.t >= finish_t:
                return CitizenActions.select_action
            state.world.agents.look_random(i_agent, multiplier)
            return action

        return action
    
    @staticmethod
    def roaming():
        # Add stop at poi logic constant finish_t ? 
        finish_t = state.t + np.random.normal(loc=10_000, scale=1_000)
        multiplier = random.choice([-1, 1])
        # target_poi_index = state.world.maps.get_target_poi_index(i_agent)
        # last_poi_index = state.last_poi_visited[i_agent]

        # while target_poi_index == last_poi_index:
        #     target_poi_index = state.world.maps.get_target_poi_index(i_agent)
        def action(i_agent: int):
            
            if state.t >= finish_t:
                return CitizenActions.select_action            
            # elif state.agent_near_poi[i_agent]:
            #     # state.agent_near_poi[i_agent] = True  # Set the flag to true when near the POI
            #     # state.last_poi_visited[i_agent] = target_poi_index
            #     return CitizenActions.stop_at_poi(i_agent)
            state.world.agents.look_random(i_agent, multiplier)
            return action
            
        return action

  

    @staticmethod
    def stop_at_poi(i_agent: int):
        state.agent_speed[i_agent,:] = 0  # Stop the agent
        # Define how long the agent will stop at the POI
        stop_duration = np.random.normal(loc=5, scale=1)  # Stop for random time
        finish_time = state.t + stop_duration
        
        # Get the attraction factor of the POI (defined between 0 and 1)
        # attraction_factor = state.world.pois.get_poi_attraction_factor(i_agent)

        # if np.random.rand() < attraction_factor: # decide whether to look at POI or not
        #     poi_position = state.world.maps.get_poi_position(i_agent)
        #     direction_to_poi = poi_position - state.agent_position[i_agent]
        #     state.agent_angle[i_agent] = np.arctan2(direction_to_poi[1], direction_to_poi[0])
        # else: # Look in random direction
        #     state.agent_angle[i_agent] = np.random.uniform(0, 2 * np.pi)
        
        def action(i_agent: int): 
            # Continue stopping until the stop duration is reached
            if state.t >= finish_time:
                return CitizenActions.move_away  # Move away from POI
            
            return action  # Keep stopping at the POI

    @staticmethod
    def social_interaction(i_agent: int):
        engagement_probability = 0.5  # Define the probability of engaging in social interaction
        # Get the positions of all citizens within a range defined as "nearby"
        in_vision = state.agents_in_vision[i_agent, :]
        for agent in in_vision:
            if np.random.rand() < engagement_probability:  # Define engagement_probability
                # Both citizens agree to interact
                return CitizenActions.stop_at_citizen(i_agent, agent)  # You may want to adjust this to reflect a stopping interaction

    @staticmethod
    def stop_at_citizen(i_agent: int, target_agent: int):
        """
        Makes the agent interact with a target agent (citizen), stopping movement once close.
        The agents look at each other, change color to yellow, and stop for a specified time.
        After the interaction, they resume moving away.
        """
        interaction_duration = 5_000  # 5 seconds in simulation time
        finish_t = state.t + interaction_duration

        # Both agents' colors change to yellow
        state.agent_colors[i_agent, :] = [255, 255, 0]  # Yellow
        state.agent_colors[target_agent, :] = [255, 255, 0]  # Yellow
        
        # Calculate the delta position between the two agents
        delta = state.agent_position[target_agent, :] - state.agent_position[i_agent, :]
        
        # If the agents are within 8 units of each other
        if np.linalg.norm(delta) < 8:
            # Make them look at each other
            angle = np.arctan2(delta[1], delta[0])
            state.agent_angle[i_agent] = angle
            state.agent_angle[target_agent] = angle + np.pi  # Opposite direction
            
            # Define the inner action that gets repeated during the interaction period
            def action(i_agent: int):
                # Stop both agents
                state.agent_speed[i_agent, :] = 0
                state.agent_speed[target_agent, :] = 0
                
                # Continue until the interaction time is over
                if state.t >= finish_t:
                    # After the interaction, both agents will move away
                    CitizenActions.move_away(i_agent)
                    CitizenActions.move_away(target_agent)
                    return CitizenActions.select_action  # Proceed to the next action after interaction
                
                # Keep returning the same action until the time is up
                return action
            
            return action


    @staticmethod
    def move_away(i_agent: int):
        state.agent_speed[i_agent,:] = 0.18
        # state.agent_near_poi[i_agent] = False   # Set flag false
        return CitizenActions.start_roaming[i_agent] # Select another action