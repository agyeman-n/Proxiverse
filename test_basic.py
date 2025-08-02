"""
Basic tests for Proxiverse.

Simple tests to validate the core functionality of entities and world engine.
"""

from entities import Entity, Resource, Agent
from world_engine import WorldEngine


def test_entity_creation():
    """Test basic entity creation and properties."""
    print("Testing entity creation...")
    
    entity = Entity(x=5, y=10)
    assert entity.x == 5
    assert entity.y == 10
    assert entity.id is not None
    print("✓ Entity creation passed")


def test_resource_functionality():
    """Test resource creation and harvesting."""
    print("Testing resource functionality...")
    
    resource = Resource(x=3, y=4, resource_type="ore", quantity=100)
    assert resource.resource_type == "ORE"
    assert resource.quantity == 100
    
    harvested = resource.harvest(30)
    assert harvested == 30
    assert resource.quantity == 70
    
    # Test over-harvesting
    harvested = resource.harvest(100)
    assert harvested == 70
    assert resource.quantity == 0
    assert resource.is_depleted()
    print("✓ Resource functionality passed")


def test_agent_inventory():
    """Test agent inventory management."""
    print("Testing agent inventory...")
    
    agent = Agent(x=0, y=0, name="TestAgent")
    assert agent.name == "TestAgent"
    assert len(agent.inventory) == 0
    
    # Test adding resources
    agent.add_to_inventory("ORE", 10)
    agent.add_to_inventory("FUEL", 5)
    assert agent.get_inventory_count("ORE") == 10
    assert agent.get_inventory_count("FUEL") == 5
    
    # Test removing resources
    removed = agent.remove_from_inventory("ORE", 3)
    assert removed == 3
    assert agent.get_inventory_count("ORE") == 7
    
    # Test production
    assert agent.can_produce_components()
    produced = agent.produce_components(2)
    assert produced == 2
    assert agent.get_inventory_count("ORE") == 5
    assert agent.get_inventory_count("FUEL") == 3
    assert agent.get_inventory_count("COMPONENTS") == 2
    print("✓ Agent inventory passed")


def test_world_engine():
    """Test world engine functionality."""
    print("Testing world engine...")
    
    world = WorldEngine(width=5, height=5)
    assert world.width == 5
    assert world.height == 5
    assert world.current_tick == 0
    
    # Test entity addition
    agent = Agent(x=2, y=2, name="TestAgent")
    success = world.add_entity(agent, 2, 2)
    assert success
    assert len(world.entities) == 1
    
    # Test entity retrieval
    entities = world.get_entity_at(2, 2)
    assert len(entities) == 1
    assert entities[0] == agent
    
    # Test movement
    success = world.move_entity(agent, 3, 3)
    assert success
    assert agent.x == 3
    assert agent.y == 3
    
    # Test tick
    world.tick()
    assert world.current_tick == 1
    print("✓ World engine passed")


def run_all_tests():
    """Run all basic tests."""
    print("=" * 40)
    print("RUNNING BASIC TESTS")
    print("=" * 40)
    
    try:
        test_entity_creation()
        test_resource_functionality()
        test_agent_inventory()
        test_world_engine()
        
        print("\n" + "=" * 40)
        print("ALL TESTS PASSED! ✓")
        print("=" * 40)
        return True
        
    except AssertionError as e:
        print(f"\nTest failed: {e}")
        return False
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        return False


if __name__ == "__main__":
    run_all_tests()
