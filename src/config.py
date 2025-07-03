"""Configuration management for Bitcoin MCP Server."""

import os
from typing import Optional
from pydantic import BaseModel, validator
from enum import Enum

class NetworkType(str, Enum):
    MAINNET = "mainnet"
    TESTNET = "testnet"
    REGTEST = "regtest"

class Config(BaseModel):
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
    
    @validator('BITCOIN_RPC_URL')
    def validate_rpc_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('Bitcoin RPC URL must start with http:// or https://')
        return v

def load_config() -> Config:
    """Load configuration from environment variables."""
    return Config(
        HOST=os.getenv('HOST', '0.0.0.0'),
        PORT=int(os.getenv('PORT', '8000')),
        DEBUG=os.getenv('DEBUG', 'false').lower() == 'true',
        BITCOIN_RPC_URL=os.getenv('BITCOIN_RPC_URL', 'https://bitcoin.two.nono.casa/'),
        BITCOIN_RPC_USER=os.getenv('BITCOIN_RPC_USER', 'user'),
        BITCOIN_RPC_PASSWORD=os.getenv('BITCOIN_RPC_PASSWORD', 'pass'),
        BITCOIN_NETWORK=NetworkType(os.getenv('BITCOIN_NETWORK', 'mainnet')),
        REQUEST_TIMEOUT=int(os.getenv('REQUEST_TIMEOUT', '30')),
        MAX_RETRIES=int(os.getenv('MAX_RETRIES', '3')),
        RATE_LIMIT_PER_MINUTE=int(os.getenv('RATE_LIMIT_PER_MINUTE', '60')),
        BLOCKCHAIR_API_KEY=os.getenv('BLOCKCHAIR_API_KEY'),
        MEMPOOL_SPACE_API_URL=os.getenv('MEMPOOL_SPACE_API_URL', 'https://mempool.space/api')
    )

# Global config instance
config = load_config()