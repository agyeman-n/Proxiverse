"""
Main server script for Proxiverse.

This script initializes the WorldEngine, EconomicEngine, and WebSocket Server,
then runs the complete networked simulation using asyncio.
"""

import asyncio
import logging
from world_engine import WorldEngine
from economic_engine import EconomicEngine
from server import Server
from entities import Resource

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_initial_world():
    """Create the initial world with some starting resources."""
    # Create a larger world for multiplayer
    world = WorldEngine(width=20, height=20)
    
    # Add some initial resources scattered around
    initial_resources = [
        (3, 3, "ORE", 80),
        (16, 4, "FUEL", 70),
        (2, 15, "ORE", 90),
        (18, 16, "FUEL", 60),
        (5, 8, "ORE", 75),
        (15, 12, "FUEL", 85),
        (8, 2, "ORE", 65),
        (12, 18, "FUEL", 80),
        (1, 10, "ORE", 70),
        (19, 8, "FUEL", 75),
    ]
    
    for x, y, resource_type, quantity in initial_resources:
        resource = Resource(x=x, y=y, resource_type=resource_type, quantity=quantity)
        world.add_entity(resource, x, y)
    
    logger.info(f"Created initial world with {len(initial_resources)} resource deposits")
    return world


async def simulation_loop(world_engine: WorldEngine, economic_engine: EconomicEngine, 
                         server: Server, tick_rate: float = 1.0):
    """
    Main simulation loop that runs the world tick and processes actions.
    
    Args:
        world_engine: The WorldEngine instance
        economic_engine: The EconomicEngine instance  
        server: The Server instance
        tick_rate: Ticks per second (default: 1 tick per second)
    """
    logger.info(f"Starting simulation loop at {tick_rate} ticks per second")
    
    tick_interval = 1.0 / tick_rate
    tick_count = 0
    
    try:
        while True:
            # Process pending actions from clients
            await server.process_action_queue()
            
            # Advance the world simulation
            world_engine.tick(economic_engine)
            
            # Send world state updates to all clients
            await server.broadcast_world_state()
            
            tick_count += 1
            
            # Log progress every 50 ticks
            if tick_count % 50 == 0:
                world_state = world_engine.get_world_state()
                logger.info(f"Simulation tick {tick_count} - "
                          f"Agents: {world_state['agents']}, "
                          f"Resources: {world_state['resources']}")
            
            # Wait for next tick
            await asyncio.sleep(tick_interval)
            
    except asyncio.CancelledError:
        logger.info("Simulation loop cancelled")
        raise
    except Exception as e:
        logger.error(f"Error in simulation loop: {e}")
        raise


async def run_server(host: str = "localhost", port: int = 8765, tick_rate: float = 1.0):
    """
    Initialize and run the complete Proxiverse server.
    
    Args:
        host: Server host address
        port: Server port number
        tick_rate: Simulation ticks per second
    """
    logger.info("=" * 60)
    logger.info("PROXIVERSE - MULTIPLAYER AI ARENA")
    logger.info("=" * 60)
    
    # Initialize game components
    world = create_initial_world()
    economic_engine = EconomicEngine(world)
    server = Server(world, economic_engine, host, port)
    
    # Show initial world state
    logger.info("=== Initial World State ===")
    world.print_world_summary()
    
    try:
        # Start the WebSocket server
        await server.start_server()
        
        # Run the server and simulation concurrently
        await asyncio.gather(
            server.server.wait_closed(),  # Keep server running
            simulation_loop(world, economic_engine, server, tick_rate)
        )
        
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    except Exception as e:
        logger.error(f"Server error: {e}")
    finally:
        # Cleanup
        logger.info("Shutting down server...")
        await server.stop_server()
        logger.info("Server shutdown complete")


def main():
    """Main entry point for the Proxiverse server."""
    try:
        # Run the async server
        asyncio.run(run_server(
            host="localhost",
            port=8765,
            tick_rate=1.0  # 1 tick per second
        ))
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Failed to start server: {e}")


if __name__ == "__main__":
    main()