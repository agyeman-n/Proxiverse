"""
WebSocket Server for Proxiverse.

This module contains the Server class that manages WebSocket connections
and facilitates communication between external AI agents and the simulation.
"""

import asyncio
import json
import websockets
import logging
from typing import Dict, Set, Optional
from websockets.server import WebSocketServerProtocol
from websockets.exceptions import InvalidUpgrade

from world_engine import WorldEngine
from economic_engine import EconomicEngine
from entities import Agent


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Server:
    """WebSocket server for handling client connections and agent communication."""
    
    def __init__(self, world_engine: WorldEngine, economic_engine: EconomicEngine, 
                 host: str = "localhost", port: int = 8765):
        """Initialize the server.
        
        Args:
            world_engine: The WorldEngine instance
            economic_engine: The EconomicEngine instance
            host: Server host address
            port: Server port number
        """
        self.world_engine = world_engine
        self.economic_engine = economic_engine
        self.host = host
        self.port = port
        
        # Track client connections and their associated agents
        self.connections: Dict[WebSocketServerProtocol, str] = {}  # websocket -> agent_id
        self.agents: Dict[str, Agent] = {}  # agent_id -> agent
        self.action_queue: asyncio.Queue = asyncio.Queue()
        
        self.server = None
        
    async def register_client(self, websocket: WebSocketServerProtocol) -> str:
        """Register a new client connection and create an agent for them.
        
        Args:
            websocket: The WebSocket connection
            
        Returns:
            The agent ID for the new client
        """
        # Find a suitable spawn position (center area)
        spawn_x = self.world_engine.width // 2
        spawn_y = self.world_engine.height // 2
        
        # Create new agent for this client
        agent_name = f"RemoteAgent_{len(self.connections) + 1}"
        agent = Agent(x=spawn_x, y=spawn_y, name=agent_name)
        
        # Add agent to world
        self.world_engine.add_entity(agent, spawn_x, spawn_y)
        
        # Track the connection and agent
        self.connections[websocket] = agent.id
        self.agents[agent.id] = agent
        
        logger.info(f"Client connected: {agent_name} (ID: {agent.id[:8]}...) at ({spawn_x}, {spawn_y})")
        
        return agent.id
    
    async def unregister_client(self, websocket: WebSocketServerProtocol):
        """Unregister a client connection and remove their agent.
        
        Args:
            websocket: The WebSocket connection to unregister
        """
        if websocket in self.connections:
            agent_id = self.connections[websocket]
            agent = self.agents.get(agent_id)
            
            if agent:
                # Remove agent from world
                self.world_engine.remove_entity(agent)
                del self.agents[agent_id]
                logger.info(f"Agent {agent.name} (ID: {agent_id[:8]}...) disconnected and removed")
            
            del self.connections[websocket]
    
    async def handle_client_message(self, websocket: WebSocketServerProtocol, message: str):
        """Handle incoming message from a client.
        
        Args:
            websocket: The WebSocket connection
            message: The JSON message from the client
        """
        try:
            data = json.loads(message)
            agent_id = self.connections.get(websocket)
            
            if not agent_id:
                await websocket.send(json.dumps({
                    "type": "error",
                    "message": "Not registered"
                }))
                return
            
            action = data.get("action")
            params = data.get("params", {})
            
            agent = self.agents.get(agent_id)
            if not agent:
                await websocket.send(json.dumps({
                    "type": "error",
                    "message": "Agent not found"
                }))
                return
            
            # Process action and send response
            try:
                logger.info(f"Processing action: {action} with params: {params}")
                
                success = False
                if action == "move":
                    dx = params.get("dx", 0)
                    dy = params.get("dy", 0)
                    success = agent.move(self.world_engine, dx, dy)
                    logger.info(f"Agent {agent.name} moved to ({agent.x}, {agent.y}) - Success: {success}")
                    
                elif action == "harvest":
                    success = agent.harvest(self.world_engine)
                    logger.info(f"Agent {agent.name} harvested at ({agent.x}, {agent.y}) - Success: {success}")
                    
                elif action == "craft":
                    success = self.economic_engine.craft_component(agent)
                    logger.info(f"Agent {agent.name} crafted component - Success: {success}")
                else:
                    logger.warning(f"Unknown action: {action}")
                    await websocket.send(json.dumps({
                        "type": "error",
                        "message": f"Unknown action: {action}"
                    }))
                    return
                
                # ALWAYS send action_confirmed first
                logger.info(f"Sending action_confirmed for {action}")
                await websocket.send(json.dumps({
                    "type": "action_confirmed",
                    "action": action,
                    "success": success
                }))
                
                # ALWAYS send game_state second
                logger.info(f"Sending game_state for {action}")
                world_state = self.world_engine.get_world_state()
                state_update = {
                    "type": "game_state",
                    "tick": world_state["tick"],
                    "agent_state": {
                        "id": agent.id,
                        "name": agent.name,
                        "x": agent.x,
                        "y": agent.y,
                        "inventory": agent.inventory
                    },
                    "world_info": {
                        "dimensions": world_state["dimensions"],
                        "total_entities": world_state["entity_count"],
                        "total_agents": world_state["agents"],
                        "total_resources": world_state["resources"]
                    }
                }
                await websocket.send(json.dumps(state_update))
                logger.info(f"Completed processing action: {action}")
                
            except Exception as e:
                logger.error(f"Error processing action {action}: {e}")
                await websocket.send(json.dumps({
                    "type": "error",
                    "message": f"Action failed: {e}"
                }))
            
        except json.JSONDecodeError:
            await websocket.send(json.dumps({
                "type": "error", 
                "message": "Invalid JSON format"
            }))
        except Exception as e:
            logger.error(f"Error handling client message: {e}")
            await websocket.send(json.dumps({
                "type": "error",
                "message": "Internal server error"
            }))
    
    async def broadcast_world_state(self):
        """Send world state updates to all connected clients."""
        if not self.connections:
            return
        
        # Prepare world state data
        world_state = self.world_engine.get_world_state()
        
        # Create a copy of connections to avoid modification during iteration
        connections_copy = list(self.connections.items())
        disconnected_clients = []
        
        for websocket, agent_id in connections_copy:
            try:
                agent = self.agents.get(agent_id)
                if not agent:
                    continue
                
                # Create personalized state update
                update = {
                    "type": "game_state",
                    "tick": world_state["tick"],
                    "agent_state": {
                        "id": agent.id,
                        "name": agent.name,
                        "x": agent.x,
                        "y": agent.y,
                        "inventory": agent.inventory
                    },
                    "world_info": {
                        "dimensions": world_state["dimensions"],
                        "total_entities": world_state["entity_count"],
                        "total_agents": world_state["agents"],
                        "total_resources": world_state["resources"]
                    }
                }
                
                await websocket.send(json.dumps(update))
                
            except websockets.exceptions.ConnectionClosed:
                disconnected_clients.append(websocket)
            except Exception as e:
                logger.error(f"Error sending state to client: {e}")
                disconnected_clients.append(websocket)
        
        # Clean up disconnected clients
        for websocket in disconnected_clients:
            await self.unregister_client(websocket)
    
    async def process_action_queue(self):
        """Process all pending actions from the action queue."""
        actions_processed = 0
        
        while not self.action_queue.empty():
            try:
                action_data = await self.action_queue.get()
                agent_id = action_data["agent_id"]
                action = action_data["action"]
                params = action_data["params"]
                
                agent = self.agents.get(agent_id)
                if not agent:
                    logger.warning(f"Agent {agent_id} not found for action {action}")
                    continue
                
                # Process different action types
                if action == "move":
                    dx = params.get("dx", 0)
                    dy = params.get("dy", 0)
                    agent.move(self.world_engine, dx, dy)
                    
                elif action == "harvest":
                    agent.harvest(self.world_engine)
                    
                elif action == "craft":
                    self.economic_engine.craft_component(agent)
                
                actions_processed += 1
                
            except Exception as e:
                logger.error(f"Error processing action: {e}")
        
        if actions_processed > 0:
            logger.debug(f"Processed {actions_processed} actions")
    
    async def handle_client(self, websocket: WebSocketServerProtocol):
        """Handle a single client connection.
        
        Args:
            websocket: The WebSocket connection
        """
        try:
            # Register the new client
            agent_id = await self.register_client(websocket)
            
            # Send welcome message
            welcome_msg = {
                "type": "connection_established",
                "agent_id": agent_id,
                "message": "Connected to Proxiverse server"
            }
            await websocket.send(json.dumps(welcome_msg))
            
            # Handle incoming messages
            async for message in websocket:
                await self.handle_client_message(websocket, message)
                
        except websockets.exceptions.ConnectionClosed:
            logger.info("Client connection closed")
        except Exception as e:
            logger.error(f"Error in client handler: {e}")
        finally:
            # Clean up when client disconnects
            await self.unregister_client(websocket)
    
    async def start_server(self):
        """Start the WebSocket server."""
        logger.info(f"Starting Proxiverse server on {self.host}:{self.port}")
        
        # Create the WebSocket server
        self.server = await websockets.serve(
            self.handle_client,
            self.host,
            self.port
        )
        
        logger.info("Proxiverse server started successfully")
        logger.info(f"WebSocket URL: ws://{self.host}:{self.port}")
        logger.info("Use test_client.py or a WebSocket client to connect")
        return self.server
    
    def _get_status_html(self):
        """Generate a simple status HTML page."""
        world_state = self.world_engine.get_world_state()
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Proxiverse Server Status</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .status {{ background: #f0f0f0; padding: 20px; border-radius: 5px; }}
                .connected {{ color: green; }}
                .disconnected {{ color: red; }}
            </style>
        </head>
        <body>
            <h1>🤖 Proxiverse AI Arena</h1>
            <div class="status">
                <h2>Server Status: <span class="connected">🟢 Online</span></h2>
                <p><strong>WebSocket URL:</strong> <code>ws://{self.host}:{self.port}/ws</code></p>
                <p><strong>Connected Agents:</strong> {len(self.connections)}</p>
                <p><strong>World Tick:</strong> {world_state['tick']}</p>
                <p><strong>Total Resources:</strong> {world_state['resources']}</p>
            </div>
            <h3>How to Connect:</h3>
            <ul>
                <li>Use <code>python test_client.py</code> to test the connection</li>
                <li>Connect your AI agent to <code>ws://{self.host}:{self.port}/ws</code></li>
                <li>Send JSON commands like: <code>{{"action": "move", "params": {{"dx": 1, "dy": 0}}}}</code></li>
            </ul>
            <h3>Available Actions:</h3>
            <ul>
                <li><code>{{"action": "move", "params": {{"dx": 1, "dy": 0}}}}</code> - Move agent</li>
                <li><code>{{"action": "harvest", "params": {{}}}}</code> - Harvest resources</li>
                <li><code>{{"action": "craft", "params": {{}}}}</code> - Craft components</li>
            </ul>
        </body>
        </html>
        """.encode('utf-8')
    
    async def stop_server(self):
        """Stop the WebSocket server."""
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            logger.info("Proxiverse server stopped")