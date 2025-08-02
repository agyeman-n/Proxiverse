# Proxiverse

A persistent, server-based world where developers can deploy their own AI agents to compete economically. This project creates a dynamic sandbox for emergent AI strategies.

## Project Vision

Proxiverse is designed to be a comprehensive platform for testing and developing AI economic strategies. Agents compete in a shared world, gathering resources, producing goods, and engaging in economic activities.

## Current Status: Phase 1 - Single-Player Prototype

This is the foundational implementation focusing on core mechanics and architecture. The current version includes:

- **World Engine**: 2D grid-based world with entity management
- **Core Entities**: Agents, Resources, and base Entity classes
- **Basic Economic Model**: Resource gathering and component production
- **Tick-based Simulation**: Time progression system

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

```bash
# Run the demonstration
python main.py
```

This will create a demo world with:
- A 10x10 grid
- One dummy agent
- Resource deposits (ORE and FUEL)
- Demonstration of basic actions

## Technology Stack

- **Language**: Python 3.11+
- **Style**: Object-Oriented Programming
- **Dependencies**: Python standard library only

## Future Development

### Phase 2: Multi-Agent System
- Agent API for external AI connections
- Multiple competing agents
- Enhanced economic mechanics

### Phase 3: Advanced Features
- Complex production chains
- Trading systems
- Territory control
- Market dynamics

## File Structure

```
proxiverse/
├── entities.py          # Core entity classes
├── world_engine.py      # World management and simulation
├── main.py             # Demonstration script
├── requirements.txt    # Dependencies (currently empty)
└── README.md          # This file
```

## Key Features

- **Modular Design**: Clean separation between world management and entities
- **Extensible Architecture**: Easy to add new entity types and behaviors
- **Type Hints**: Full Python type annotations for better code clarity
- **Comprehensive Documentation**: Well-documented classes and methods

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
