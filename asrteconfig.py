"""
Configuration management for ASRTE.
Centralized configuration with environment variable support.
"""
import os
import json
import logging
from dataclasses import dataclass
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class FirebaseConfig:
    """Firebase configuration with validation."""
    service_account_path: str
    project_id: str
    database_url: str
    
    def __post_init__(self):
        """Validate Firebase configuration on initialization."""
        if not Path(self.service_account_path).exists():
            raise FileNotFoundError(
                f"Firebase service account file not found: {self.service_account_path}"
            )
        if not self.project_id or len(self.project_id) < 3:
            raise ValueError("Firebase project_id must be provided and valid")


@dataclass
class TradingConfig:
    """Trading-specific configuration."""
    exchange: str = "binance"
    symbols: tuple = ("BTC/USDT", "ETH/USDT")
    timeframe: str = "1h"
    initial_capital: float = 10000.0
    max_drawdown: float = 0.25  # 25% max drawdown
    min_confidence: float = 0.7  # Minimum confidence for execution


class Config:
    """Main configuration manager for ASRTE."""
    
    _instance: Optional['Config'] = None
    
    def __new__(cls):
        """Singleton pattern for configuration."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._load_environment()
        self.firebase: FirebaseConfig = self._load_firebase_config()
        self.trading: TradingConfig = TradingConfig()
        self.log_level: str = os.getenv("ASRTE_LOG_LEVEL", "INFO")
        self.data_cache_dir: Path = Path(os.getenv("ASRTE_CACHE_DIR", "./data_cache"))
        
        # Ensure cache directory exists
        self.data_cache_dir.mkdir(exist_ok=True, parents=True)
        
        self._initialized = True
        logger.info("Configuration initialized successfully")
    
    def _load_environment(self) -> None:
        """Load environment variables from .env file if present."""
        env_path = Path(".env")
        if env_path.exists():
            try:
                from dotenv import load_dotenv
                load_dotenv(env_path)
                logger.debug("Loaded environment variables from .env")
            except ImportError:
                logger.warning("python-dotenv not installed, skipping .env load")
    
    def _load_firebase_config(self) -> FirebaseConfig:
        """Load and validate Firebase configuration."""
        service_account_path = os.getenv(
            "FIREBASE_SERVICE_ACCOUNT",
            "./firebase-service-account.json"
        )
        
        project_id = os.getenv("FIREBASE_PROJECT_ID")
        database_url = os.getenv("FIREBASE_DATABASE_URL")
        
        if not project_id or not database_url:
            raise EnvironmentError(
                "FIREBASE_PROJECT_ID and FIREBASE_DATABASE_URL must be set"
            )
        
        return FirebaseConfig(
            service_account_path=service_account_path,
            project_id=project_id,
            database_url=database_url
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Return configuration as dictionary (for logging/debugging)."""
        return {
            "firebase": {
                "project_id": self.firebase.project_id,
                "database_url": self.firebase.database_url
            },
            "trading": {
                "exchange": self.trading.exchange,
                "symbols": self.trading.symbols,
                "timeframe": self.trading.timeframe
            },
            "log_level": self.log_level,
            "data_cache_dir": str(self.data_cache_dir)
        }