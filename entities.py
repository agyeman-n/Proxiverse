"""
Core entity classes for Proxiverse.

This module defines the fundamental entities that exist within the simulation world:
- Entity: Base class for all objects in the world
- Resource: Represents raw materials and resources
- Agent: Represents AI-controlled entities with inventories
"""

from typing import Dict, Any, Optional
import uuid


class Entity:
    """
    Base class for all entities in the simulation world.
    
    Every entity has a unique identifier and a position in the 2D world grid.
    """
    
    def __init__(self, x: int, y: int, entity_id: Optional[str] = None):
        """
        Initialize an entity with position and unique ID.
        
        Args:
            x: X coordinate in the world grid
            y: Y coordinate in the world grid
            entity_id: Optional unique identifier. If None, generates a UUID.
        """
        self.id = entity_id or str(uuid.uuid4())
        self.x = x
        self.y = y
    
    def move_to(self, x: int, y: int) -> None:
        """Move the entity to a new position."""
        self.x = x
        self.y = y
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id[:8]}..., x={self.x}, y={self.y})"


class Resource(Entity):
    """
    Represents a resource entity in the world.
    
    Resources are collectible items that agents can gather and use for production.
    Examples include ORE, FUEL, and COMPONENTS.
    """
    
    def __init__(self, x: int, y: int, resource_type: str, quantity: int, entity_id: Optional[str] = None):
        """
        Initialize a resource entity.
        
        Args:
            x: X coordinate in the world grid
            y: Y coordinate in the world grid
            resource_type: Type of resource (e.g., 'ORE', 'FUEL', 'COMPONENTS')
            quantity: Amount of this resource
            entity_id: Optional unique identifier
        """
        super().__init__(x, y, entity_id)
        self.resource_type = resource_type.upper()
        self.quantity = quantity
    
    def harvest(self, amount: int) -> int:
        """
        Harvest a specified amount from this resource.
        
        Args:
            amount: Desired amount to harvest
            
        Returns:
            Actual amount harvested (may be less than requested)
        """
        harvested = min(amount, self.quantity)
        self.quantity -= harvested
        return harvested
    
    def is_depleted(self) -> bool:
        """Check if this resource is completely depleted."""
        return self.quantity <= 0
    
    def __repr__(self) -> str:
        return f"Resource(id={self.id[:8]}..., type={self.resource_type}, qty={self.quantity}, x={self.x}, y={self.y})"


class Agent(Entity):
    """
    Represents an AI agent in the simulation.
    
    Agents can move around the world, collect resources, and perform economic actions.
    Each agent has an inventory to store collected resources.
    """
    
    def __init__(self, x: int, y: int, name: str, entity_id: Optional[str] = None):
        """
        Initialize an agent.
        
        Args:
            x: X coordinate in the world grid
            y: Y coordinate in the world grid
            name: Display name for the agent
            entity_id: Optional unique identifier
        """
        super().__init__(x, y, entity_id)
        self.name = name
        self.inventory: Dict[str, int] = {}  # resource_type -> quantity
    
    def add_to_inventory(self, resource_type: str, quantity: int) -> None:
        """
        Add resources to the agent's inventory.
        
        Args:
            resource_type: Type of resource to add
            quantity: Amount to add
        """
        resource_type = resource_type.upper()
        if resource_type in self.inventory:
            self.inventory[resource_type] += quantity
        else:
            self.inventory[resource_type] = quantity
    
    def remove_from_inventory(self, resource_type: str, quantity: int) -> int:
        """
        Remove resources from the agent's inventory.
        
        Args:
            resource_type: Type of resource to remove
            quantity: Amount to remove
            
        Returns:
            Actual amount removed (may be less than requested)
        """
        resource_type = resource_type.upper()
        if resource_type not in self.inventory:
            return 0
        
        available = self.inventory[resource_type]
        removed = min(quantity, available)
        self.inventory[resource_type] -= removed
        
        # Clean up empty entries
        if self.inventory[resource_type] == 0:
            del self.inventory[resource_type]
        
        return removed
    
    def get_inventory_count(self, resource_type: str) -> int:
        """
        Get the quantity of a specific resource in inventory.
        
        Args:
            resource_type: Type of resource to check
            
        Returns:
            Quantity of the resource (0 if not present)
        """
        return self.inventory.get(resource_type.upper(), 0)
    
    def can_produce_components(self) -> bool:
        """
        Check if agent has enough resources to produce components.
        Requires at least 1 ORE and 1 FUEL.
        """
        return self.get_inventory_count('ORE') >= 1 and self.get_inventory_count('FUEL') >= 1
    
    def produce_components(self, quantity: int = 1) -> int:
        """
        Produce components from ORE and FUEL.
        
        Args:
            quantity: Number of components to produce
            
        Returns:
            Actual number of components produced
        """
        max_producible = min(
            self.get_inventory_count('ORE'),
            self.get_inventory_count('FUEL'),
            quantity
        )
        
        if max_producible > 0:
            self.remove_from_inventory('ORE', max_producible)
            self.remove_from_inventory('FUEL', max_producible)
            self.add_to_inventory('COMPONENTS', max_producible)
        
        return max_producible
    
    def __repr__(self) -> str:
        return f"Agent(id={self.id[:8]}..., name={self.name}, x={self.x}, y={self.y}, inventory={self.inventory})"
