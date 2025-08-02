"""
Proxiverse

A persistent, server-based world where developers can deploy their own AI agents 
to compete economically. This package provides the foundational components for 
building complex AI economic simulations.
"""

from .entities import Entity, Resource, Agent
from .world_engine import WorldEngine
from .economic_engine import EconomicEngine
from .server import Server

__version__ = "2.0.0"
__author__ = "Proxiverse Team"

__all__ = ["Entity", "Resource", "Agent", "WorldEngine", "EconomicEngine", "Server"]
