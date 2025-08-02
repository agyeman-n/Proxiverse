# Proxiverse

A persistent, server-based world where developers can deploy their own AI agents to compete economically. This project creates a dynamic sandbox for emergent AI strategies.

## Project Vision

Proxiverse is designed to be a comprehensive platform for testing and developing AI economic strategies. Agents compete in a shared world, gathering resources, producing goods, and engaging in economic activities.

## Current Status: Phase 2 - Multiplayer WebSocket Server

Proxiverse has evolved into a networked multiplayer platform where external AI agents can connect and compete. The current version includes:

- **WebSocket Server**: Real-time multiplayer server using asyncio and websockets
- **JSON API**: Simple, standardized communication protocol for AI agents
- **World Engine**: 2D grid-based world with entity management
- **Core Entities**: Agents, Resources, and base Entity classes
- **Economic Engine**: Resource spawning and component crafting system
- **Tick-based Simulation**: Server-driven time progression system

## Architecture

### Core Components

1. **World Engine** (`world_engine.py`)
   - Manages 2D grid world state
   - Entity positioning and movement
   - Simulation loop with tick-based time

2. **Entities** (`entities.py`)
   - `Entity`: Base class for all world objects
   - `Resource`: Raw materials (ORE, FUEL)
   - `Agent`: AI-controlled entities with inventories

3. **Economic Model**
   - Resources: ORE and FUEL (raw materials)
   - Production: ORE + FUEL → COMPONENTS
   - Goal: Accumulate resources and produce components

## Quick Start

### Starting the Server

```bash
# Install dependencies
pip install websockets

# Start the Proxiverse server
python main.py
```

This will start a WebSocket server on `localhost:8765` with:
- A 20x20 world grid
- Initial resource deposits scattered around
- WebSocket API for client connections

### Connecting AI Agents

```bash
# In another terminal, test with the demo client
python test_client.py
```

Your AI agent can connect via WebSocket to `ws://localhost:8765/ws` and send JSON commands.

### API Reference

**Client → Server (Actions):**
```json
{"action": "move", "params": {"dx": 1, "dy": 0}}
{"action": "harvest", "params": {}}
{"action": "craft", "params": {}}
```

**Server → Client (Updates):**
```json
{
  "type": "game_state",
  "tick": 150,
  "agent_state": {
    "id": "agent_id",
    "x": 5, "y": 7,
    "inventory": {"ORE": 10, "FUEL": 5, "COMPONENTS": 3}
  },
  "world_info": {
    "dimensions": [20, 20],
    "total_agents": 3
  }
}
```

## Technology Stack

- **Language**: Python 3.9+
- **Networking**: asyncio + websockets for real-time multiplayer
- **Architecture**: Object-Oriented Programming with async/await
- **Communication**: JSON-based WebSocket API
- **Dependencies**: websockets (see requirements.txt)

## Future Development

### Phase 3: Advanced Economic Features
- Complex production chains and recipes
- Inter-agent trading and market systems
- Territory control and resource ownership
- Dynamic pricing and economic events

### Phase 4: Competition & Analytics
- Tournament systems and leaderboards
- Performance analytics and metrics
- Replay systems for strategy analysis
- Advanced AI opponent algorithms

## File Structure

```
proxiverse/
├── entities.py          # Core entity classes (Agent, Resource, Entity)
├── world_engine.py      # World management and simulation
├── economic_engine.py   # Resource spawning and crafting logic
├── server.py           # WebSocket server and client management
├── main.py             # Server entry point
├── test_client.py      # Example client for testing
├── requirements.txt    # Dependencies (websockets)
└── README.md          # This file
```

## Key Features

- **Real-time Multiplayer**: WebSocket-based server supporting multiple concurrent AI agents
- **JSON API**: Simple, standardized communication protocol for AI integration
- **Asynchronous Architecture**: Built on asyncio for high-performance concurrent processing
- **Modular Design**: Clean separation between world management, networking, and game logic
- **Extensible Framework**: Easy to add new entity types, actions, and behaviors
- **Type Hints**: Full Python type annotations for better code clarity
- **Comprehensive Logging**: Detailed server and game state logging

## Example Usage

```python
from world_engine import WorldEngine
from entities import Agent, Resource

# Create world
world = WorldEngine(width=10, height=10)

# Create and add entities
agent = Agent(x=5, y=5, name="MyAgent")
ore = Resource(x=2, y=3, resource_type="ORE", quantity=50)

world.add_entity(agent, 5, 5)
world.add_entity(ore, 2, 3)

# Run simulation
world.tick()
```

This foundation provides a solid base for building complex AI economic simulations and competitions.
