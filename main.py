"""
Main simulation script for Proxiverse.

This script initializes the WorldEngine and EconomicEngine, creates an agent,
and runs a complete simulation loop to demonstrate the AI economic simulation.
"""

from world_engine import WorldEngine
from economic_engine import EconomicEngine
from entities import Agent, Resource
import random


def create_initial_world():
    """Create the initial world with some resources and an agent."""
    # Create a 15x15 world for more space
    world = WorldEngine(width=15, height=15)
    
    # Create an agent at the center
    agent = Agent(x=7, y=7, name="ProxiverseAgent")
    world.add_entity(agent, 7, 7)
    
    # Add some initial resources scattered around
    initial_resources = [
        (2, 3, "ORE", 50),
        (12, 4, "FUEL", 40),
        (5, 10, "ORE", 60),
        (10, 12, "FUEL", 35),
        (3, 8, "ORE", 45),
        (13, 7, "FUEL", 55),
    ]
    
    for x, y, resource_type, quantity in initial_resources:
        resource = Resource(x=x, y=y, resource_type=resource_type, quantity=quantity)
        world.add_entity(resource, x, y)
    
    return world, agent


def run_simulation(num_ticks=200):
    """Run the complete simulation for the specified number of ticks."""
    print("=" * 60)
    print("PROXIVERSE - AI ECONOMIC SIMULATION")
    print("=" * 60)
    print(f"Running simulation for {num_ticks} ticks...")
    print()
    
    # Initialize world and engines
    world, agent = create_initial_world()
    economic_engine = EconomicEngine(world)
    
    # Show initial state
    print("=== Initial World State ===")
    world.print_world_summary()
    print(f"Agent starting inventory: {agent.inventory}")
    print()
    
    # Run simulation loop
    print("=== Running Simulation ===")
    for tick in range(1, num_ticks + 1):
        world.tick(economic_engine)
        
        # Print progress every 50 ticks
        if tick % 50 == 0:
            print(f"Completed {tick}/{num_ticks} ticks...")
    
    # Show final state
    print("\n=== Final World State ===")
    world.print_world_summary()
    print(f"Agent final inventory: {agent.inventory}")
    print(f"Agent final position: ({agent.x}, {agent.y})")
    
    # Calculate agent's success
    total_components = agent.get_inventory_count("COMPONENTS")
    total_ore = agent.get_inventory_count("ORE")
    total_fuel = agent.get_inventory_count("FUEL")
    
    print(f"\n=== Agent Performance Summary ===")
    print(f"Components crafted: {total_components}")
    print(f"Ore collected: {total_ore}")
    print(f"Fuel collected: {total_fuel}")
    print(f"Total resources in inventory: {sum(agent.inventory.values())}")
    
    if total_components > 0:
        print(f"Success! Agent crafted {total_components} components!")
    else:
        print("Agent did not craft any components.")
    
    print("\nSimulation completed successfully!")


if __name__ == "__main__":
    run_simulation()
