from agent.agent import Agent

from world.world import World
from visualization.visualization import Visualization


def main():
    """
    This function runs the simulation of the agents moving in the environment.
    """
    # Create a world
    world = World(1000)

    # Add agents to the world
    agent1 = Agent(0, 0, 'red', world)
    agent2 = Agent(10,10, 'blue', world)
    world.add_agent(agent1)
    world.add_agent(agent2)

    # Create a visualization object
    vis = Visualization(world)

    vis.run()

    # Close the visualization
    vis.close()

if __name__ == "__main__":
    # Set up signal handler before calling main()
    main()
