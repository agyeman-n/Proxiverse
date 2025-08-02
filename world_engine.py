"""
World Engine for Proxiverse.

This module contains the core WorldEngine class that manages the simulation world,
entity positioning, and the main simulation loop.
"""

from typing import List, Optional, Dict, Set
from entities import Entity, Resource, Agent


class WorldEngine:
    """
    The foundational layer that manages the state of the world.
    
    Manages a 2D grid world, entity positions, and the core simulation loop
    with tick-based time progression.
    """
    
    def __init__(self, width: int, height: int):
        """
        Initialize the world engine with specified dimensions.
        
        Args:
            width: Width of the world grid
            height: Height of the world grid
        """
        self.width = width
        self.height = height
        self.current_tick = 0
        
        # Initialize the 2D world grid - each cell contains a list of entities
        self.grid: List[List[List[Entity]]] = []
        for y in range(height):
            row = []
            for x in range(width):
                row.append([])  # Each cell is a list of entities
            self.grid.append(row)
        
        # Keep track of all entities by ID for efficient lookup
        self.entities: Dict[str, Entity] = {}
        
        # Track entity positions for efficient updates
        self.entity_positions: Dict[str, tuple] = {}  # entity_id -> (x, y)
    
    def is_valid_position(self, x: int, y: int) -> bool:
        """
        Check if the given coordinates are within the world bounds.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            True if position is valid, False otherwise
        """
        return 0 <= x < self.width and 0 <= y < self.height
    
    def add_entity(self, entity: Entity, x: int, y: int) -> bool:
        """
        Add an entity to the world at the specified position.
        
        Args:
            entity: The entity to add
            x: X coordinate
            y: Y coordinate
            
        Returns:
            True if entity was successfully added, False otherwise
        """
        if not self.is_valid_position(x, y):
            return False
        
        if entity.id in self.entities:
            return False  # Entity already exists
        
        # Update entity position
        entity.move_to(x, y)
        
        # Add to grid
        self.grid[y][x].append(entity)
        
        # Add to tracking dictionaries
        self.entities[entity.id] = entity
        self.entity_positions[entity.id] = (x, y)
        
        return True
    
    def remove_entity(self, entity: Entity) -> bool:
        """
        Remove an entity from the world.
        
        Args:
            entity: The entity to remove
            
        Returns:
            True if entity was successfully removed, False otherwise
        """
        if entity.id not in self.entities:
            return False
        
        # Get current position
        x, y = self.entity_positions[entity.id]
        
        # Remove from grid
        if entity in self.grid[y][x]:
            self.grid[y][x].remove(entity)
        
        # Remove from tracking dictionaries
        del self.entities[entity.id]
        del self.entity_positions[entity.id]
        
        return True
    
    def move_entity(self, entity: Entity, new_x: int, new_y: int) -> bool:
        """
        Move an entity to a new position.
        
        Args:
            entity: The entity to move
            new_x: New X coordinate
            new_y: New Y coordinate
            
        Returns:
            True if entity was successfully moved, False otherwise
        """
        if not self.is_valid_position(new_x, new_y):
            return False
        
        if entity.id not in self.entities:
            return False
        
        # Get current position
        old_x, old_y = self.entity_positions[entity.id]
        
        # Remove from old position
        self.grid[old_y][old_x].remove(entity)
        
        # Add to new position
        self.grid[new_y][new_x].append(entity)
        
        # Update tracking
        entity.move_to(new_x, new_y)
        self.entity_positions[entity.id] = (new_x, new_y)
        
        return True
    
    def get_entity_at(self, x: int, y: int) -> List[Entity]:
        """
        Get all entities at the specified position.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            List of entities at the position (empty list if none or invalid position)
        """
        if not self.is_valid_position(x, y):
            return []
        
        return self.grid[y][x].copy()  # Return a copy to prevent external modification
    
    def get_entities_by_type(self, entity_type: type) -> List[Entity]:
        """
        Get all entities of a specific type.
        
        Args:
            entity_type: The type of entity to search for
            
        Returns:
            List of entities of the specified type
        """
        # Create a copy of entities values to avoid modification during iteration
        entities_copy = list(self.entities.values())
        return [entity for entity in entities_copy if isinstance(entity, entity_type)]
    
    def get_nearby_entities(self, x: int, y: int, radius: int = 1) -> List[Entity]:
        """
        Get all entities within a certain radius of a position.
        
        Args:
            x: Center X coordinate
            y: Center Y coordinate
            radius: Search radius (default 1 for adjacent cells)
            
        Returns:
            List of entities within the radius
        """
        nearby_entities = []
        
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                check_x, check_y = x + dx, y + dy
                if self.is_valid_position(check_x, check_y):
                    nearby_entities.extend(self.get_entity_at(check_x, check_y))
        
        return nearby_entities
    
    def tick(self, economic_engine=None) -> None:
        """
        Advance the simulation by one tick.
        
        This is the main simulation loop method that handles entity updates,
        resource management, and game logic. Agent actions are now processed
        externally through the server's action queue.
        
        Args:
            economic_engine: Optional EconomicEngine instance for resource spawning
        """
        self.current_tick += 1
        
        # Spawn resources periodically if economic engine is provided
        if economic_engine and economic_engine.should_spawn_resources():
            economic_engine.spawn_resources()
        
        # Note: Agent actions are now processed by the server before tick()
        # The tick method focuses on world state updates and resource management
        
        print(f"Tick {self.current_tick}: World ticked.")
    
    def get_world_state(self) -> Dict:
        """
        Get a snapshot of the current world state.
        
        Returns:
            Dictionary containing world information
        """
        return {
            'tick': self.current_tick,
            'dimensions': (self.width, self.height),
            'entity_count': len(self.entities),
            'agents': len(self.get_entities_by_type(Agent)),
            'resources': len(self.get_entities_by_type(Resource))
        }
    
    def print_world_summary(self) -> None:
        """Print a summary of the current world state."""
        state = self.get_world_state()
        print(f"\n=== World Summary (Tick {state['tick']}) ===")
        print(f"Dimensions: {state['dimensions'][0]}x{state['dimensions'][1]}")
        print(f"Total Entities: {state['entity_count']}")
        print(f"Agents: {state['agents']}")
        print(f"Resources: {state['resources']}")
        print("=" * 35)
    
    def __repr__(self) -> str:
        return f"WorldEngine(width={self.width}, height={self.height}, tick={self.current_tick}, entities={len(self.entities)})"
