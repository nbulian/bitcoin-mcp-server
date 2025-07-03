"""Configuration management for Bitcoin MCP Server."""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import validator
from enum import Enum

class NetworkType(str, Enum):
    MAINNET = "mainnet"
    TESTNET = "testnet"
    REGTEST = "regtest"

class Config(BaseSettings):
    """Application configuration."""
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    
    # Bitcoin RPC Configuration
    BITCOIN_RPC_URL: str = "https://bitcoin.two.nono.casa/"
    BITCOIN_RPC_USER: str = "user"
    BITCOIN_RPC_PASSWORD: str = "pass"
    BITCOIN_NETWORK: NetworkType = NetworkType.MAINNET
    
    # API Configuration
    REQUEST_TIMEOUT: int = 30
    MAX_RETRIES: int = 3
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # External APIs (optional)
    BLOCKCHAIR_API_KEY: Optional[str] = None
    MEMPOOL_SPACE_API_URL: str = "https://mempool.space/api"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    @validator('BITCOIN_RPC_URL')
    def validate_rpc_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('Bitcoin RPC URL must start with http:// or https://')
        return v

# Global config instance
config = Config()