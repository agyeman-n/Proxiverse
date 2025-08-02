"""
Main demonstration script for Proxiverse.

This script shows how to use the WorldEngine and entity classes
to create a basic simulation scenario.
"""

from world_engine import WorldEngine
from entities import Agent, Resource


def create_demo_world():
    """Create a demonstration world with some initial entities."""
    # Create a 10x10 world
    world = WorldEngine(width=10, height=10)
    
    # Create a dummy agent
    agent = Agent(x=5, y=5, name="DummyAgent")
    world.add_entity(agent, 5, 5)
    
    # Add some resources to the world
    ore_deposit = Resource(x=2, y=3, resource_type="ORE", quantity=50)
    fuel_deposit = Resource(x=7, y=8, resource_type="FUEL", quantity=30)
    
    world.add_entity(ore_deposit, 2, 3)
    world.add_entity(fuel_deposit, 7, 8)
    
    return world, agent


def demonstrate_basic_actions(world, agent):
    """Demonstrate basic agent actions."""
    print("\n=== Demonstrating Basic Agent Actions ===")
    
    # Show initial state
    print(f"Agent initial state: {agent}")
    
    # Move agent to ore deposit
    print(f"\nMoving agent to ore deposit at (2, 3)...")
    world.move_entity(agent, 2, 3)
    print(f"Agent position: ({agent.x}, {agent.y})")
    
    # Check what's at the agent's position
    entities_here = world.get_entity_at(agent.x, agent.y)
    print(f"Entities at agent position: {entities_here}")
    
    # Simulate harvesting ore
    for entity in entities_here:
        if isinstance(entity, Resource) and entity.resource_type == "ORE":
            harvested = entity.harvest(10)
            agent.add_to_inventory("ORE", harvested)
            print(f"Harvested {harvested} ORE")
            break
    
    print(f"Agent after harvesting: {agent}")
    
    # Move to fuel deposit
    print(f"\nMoving agent to fuel deposit at (7, 8)...")
    world.move_entity(agent, 7, 8)
    
    # Harvest fuel
    entities_here = world.get_entity_at(agent.x, agent.y)
    for entity in entities_here:
        if isinstance(entity, Resource) and entity.resource_type == "FUEL":
            harvested = entity.harvest(5)
            agent.add_to_inventory("FUEL", harvested)
            print(f"Harvested {harvested} FUEL")
            break
    
    print(f"Agent after harvesting fuel: {agent}")
    
    # Produce components
    if agent.can_produce_components():
        produced = agent.produce_components(3)
        print(f"Produced {produced} COMPONENTS")
        print(f"Agent final state: {agent}")
    else:
        print("Agent cannot produce components - insufficient resources")


def run_simulation_demo():
    """Run a complete demonstration of the simulation."""
    print("=" * 50)
    print("PROXIVERSE - PHASE 1 DEMO")
    print("=" * 50)
    
    # Create the world
    world, agent = create_demo_world()
    
    # Show initial world state
    world.print_world_summary()
    
    # Demonstrate basic actions
    demonstrate_basic_actions(world, agent)
    
    # Run some simulation ticks
    print("\n=== Running Simulation Ticks ===")
    for i in range(5):
        world.tick()
    
    # Show final world state
    world.print_world_summary()
    
    print("\nDemo completed successfully!")


if __name__ == "__main__":
    run_simulation_demo()
