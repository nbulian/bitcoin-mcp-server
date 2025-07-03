"""Custom error classes for Bitcoin MCP Server."""

from typing import Dict, Any, Optional

class BitcoinMCPError(Exception):
    """Base exception for Bitcoin MCP Server."""
    
    def __init__(self, message: str, code: int = -32000, data: Optional[Dict[str, Any]] = None):
        self.message = message
        self.code = code
        self.data = data
        super().__init__(message)
    
    def to_json_rpc_error(self) -> Dict[str, Any]:
        """Convert to JSON-RPC error format."""
        error = {
            "code": self.code,
            "message": self.message
        }
        if self.data:
            error["data"] = self.data
        return error

class BitcoinRPCError(BitcoinMCPError):
    """Bitcoin RPC related error."""
    pass

class ValidationError(BitcoinMCPError):
    """Input validation error."""
    
    def __init__(self, message: str, field: str = None):
        super().__init__(message, -32602)
        if field:
            self.data = {"field": field}

class NetworkError(BitcoinMCPError):
    """Network connectivity error."""
    
    def __init__(self, message: str):
        super().__init__(message, -32003)

class RateLimitError(BitcoinMCPError):
    """Rate limit exceeded error."""
    
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, -32004)