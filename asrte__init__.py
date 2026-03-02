"""
Autonomous Self-Reinforcing Trading Ecosystem (ASRTE)
Core package for self-evolving trading strategies.
"""

__version__ = "1.0.0"
__author__ = "ASRTE Architect"

# Core components
from .config import Config
from .database import DatabaseManager
from .master_agent import MasterAgent

__all__ = ["Config", "DatabaseManager", "MasterAgent"]