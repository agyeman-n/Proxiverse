"""
Test client for Proxiverse WebSocket server.

This script demonstrates how to connect to the Proxiverse server
and send basic commands to control an agent.
"""

import asyncio
import json
import websockets
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_client():
    """Test client that connects to the server and sends some basic commands."""
    uri = "ws://localhost:8765"
    
    try:
        logger.info(f"Connecting to Proxiverse server at {uri}")
        
        async with websockets.connect(uri) as websocket:
            # Wait for welcome message
            welcome_msg = await websocket.recv()
            welcome_data = json.loads(welcome_msg)
            logger.info(f"Connected! Agent ID: {welcome_data.get('agent_id', 'Unknown')}")
            
            # Send some test commands
            commands = [
                {"action": "move", "params": {"dx": 1, "dy": 0}},
                {"action": "move", "params": {"dx": 0, "dy": 1}},
                {"action": "harvest", "params": {}},
                {"action": "move", "params": {"dx": -1, "dy": 0}},
                {"action": "craft", "params": {}},
            ]
            
            for i, command in enumerate(commands):
                logger.info(f"Sending command {i+1}: {command}")
                await websocket.send(json.dumps(command))
                
                # Wait a bit between commands
                await asyncio.sleep(2)
                
                # Try to receive any server messages
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=0.5)
                    response_data = json.loads(response)
                    logger.info(f"Server response: {response_data['type']}")
                    if response_data['type'] == 'game_state':
                        agent_state = response_data['agent_state']
                        logger.info(f"Agent position: ({agent_state['x']}, {agent_state['y']})")
                        logger.info(f"Agent inventory: {agent_state['inventory']}")
                except asyncio.TimeoutError:
                    logger.info("No immediate response from server")
            
            logger.info("Test commands completed. Staying connected for a few more seconds...")
            await asyncio.sleep(5)
            
    except websockets.exceptions.InvalidMessage:
        logger.error("Could not connect to server. Make sure the server is running.")
    except websockets.exceptions.ConnectionClosedError:
        logger.error("Connection closed unexpectedly.")
    except ConnectionRefusedError:
        logger.error("Could not connect to server. Make sure the server is running.")
    except Exception as e:
        logger.error(f"Error: {e}")


async def main():
    """Main function to run the test client."""
    await test_client()


if __name__ == "__main__":
    asyncio.run(main())