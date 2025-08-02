"""
Economic Engine for Proxiverse.

This module contains the EconomicEngine class that manages economic activities
such as resource spawning and component crafting.
"""

import random
from typing import List
from world_engine import WorldEngine
from entities import Agent, Resource


class EconomicEngine:
    """Manages economic activities in the simulation world."""
    
    def __init__(self, world_engine: WorldEngine):
        """Initialize the EconomicEngine with a reference to the world engine.
        
        Args:
            world_engine: The WorldEngine instance to manage
        """
        self.world_engine = world_engine
        self.spawn_tick_counter = 0
        self.spawn_interval = 10  # Spawn resources every 10 ticks
    
    def spawn_resources(self, max_resources: int = 50) -> None:
        """Spawn new resources in the world if below the maximum.
        
        Args:
            max_resources: Maximum number of resources allowed in the world
        """
        # Count current resources
        current_resources = len(self.world_engine.get_entities_by_type(Resource))
        
        if current_resources >= max_resources:
            return
        
        # Find empty cells
        empty_cells = []
        for x in range(self.world_engine.width):
            for y in range(self.world_engine.height):
                entities_here = self.world_engine.get_entity_at(x, y)
                if not entities_here:  # Cell is empty
                    empty_cells.append((x, y))
        
        if not empty_cells:
            return  # No empty cells available
        
        # Determine how many resources to spawn
        resources_to_spawn = min(max_resources - current_resources, len(empty_cells))
        
        for _ in range(resources_to_spawn):
            # Randomly select an empty cell
            x, y = random.choice(empty_cells)
            empty_cells.remove((x, y))  # Remove from available cells
            
            # Randomly choose resource type and quantity
            resource_type = random.choice(["ORE", "FUEL"])
            quantity = random.randint(20, 100)
            
            # Create and add the resource
            resource = Resource(x=x, y=y, resource_type=resource_type, quantity=quantity)
            self.world_engine.add_entity(resource, x, y)
    
    def craft_component(self, agent: Agent) -> bool:
        """Craft a component from the agent's inventory if possible.
        
        Args:
            agent: The agent attempting to craft a component
            
        Returns:
            True if component was successfully crafted, False otherwise
        """
        # Check if agent has required materials
        ore_count = agent.get_inventory_count("ORE")
        fuel_count = agent.get_inventory_count("FUEL")
        
        if ore_count >= 1 and fuel_count >= 1:
            # Remove materials from inventory
            agent.remove_from_inventory("ORE", 1)
            agent.remove_from_inventory("FUEL", 1)
            
            # Add component to inventory
            agent.add_to_inventory("COMPONENTS", 1)
            
            return True
        
        return False
    
    def should_spawn_resources(self) -> bool:
        """Check if it's time to spawn resources based on tick counter.
        
        Returns:
            True if resources should be spawned this tick
        """
        self.spawn_tick_counter += 1
        if self.spawn_tick_counter >= self.spawn_interval:
            self.spawn_tick_counter = 0
            return True
        return False 