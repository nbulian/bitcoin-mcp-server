"""Bitcoin RPC client implementation."""

import json
import asyncio
from typing import Dict, Any, Optional, List
import httpx
from datetime import datetime, timedelta

from .config import config
from .utils.errors import BitcoinRPCError, NetworkError, RateLimitError

class BitcoinRPCClient:
    """Async Bitcoin RPC client with rate limiting and error handling."""
    
    def __init__(self):
        self.base_url = config.BITCOIN_RPC_URL
        self.auth = (config.BITCOIN_RPC_USER, config.BITCOIN_RPC_PASSWORD)
        self.timeout = config.REQUEST_TIMEOUT
        self.max_retries = config.MAX_RETRIES
        
        # Rate limiting
        self.request_times: List[datetime] = []
        self.rate_limit = config.RATE_LIMIT_PER_MINUTE
        
        # HTTP client
        self.client = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.client = httpx.AsyncClient(
            auth=self.auth,
            timeout=httpx.Timeout(self.timeout),
            headers={"Content-Type": "application/json"}
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.client:
            await self.client.aclose()
    
    def _check_rate_limit(self):
        """Check if we're within rate limits."""
        now = datetime.utcnow()
        # Remove requests older than 1 minute
        self.request_times = [
            req_time for req_time in self.request_times 
            if now - req_time < timedelta(minutes=1)
        ]
        
        if len(self.request_times) >= self.rate_limit:
            raise RateLimitError(f"Rate limit of {self.rate_limit} requests per minute exceeded")
        
        self.request_times.append(now)
    
    async def _make_request(self, method: str, params: List[Any] = None) -> Dict[str, Any]:
        """
        Make a JSON-RPC request to Bitcoin node.
        
        Args:
            method: RPC method name
            params: Method parameters
        
        Returns:
            Dict containing the RPC response
        
        Raises:
            BitcoinRPCError: If RPC call fails
            NetworkError: If network request fails
            RateLimitError: If rate limit exceeded
        """
        self._check_rate_limit()
        
        if params is None:
            params = []
        
        payload = {
            "jsonrpc": "1.0",
            "id": "bitcoin-mcp",
            "method": method,
            "params": params
        }
        
        last_error = None
        for attempt in range(self.max_retries):
            try:
                response = await self.client.post(
                    self.base_url,
                    json=payload
                )
                response.raise_for_status()
                
                result = response.json()
                
                if result.get("error"):
                    error = result["error"]
                    raise BitcoinRPCError(
                        f"RPC Error: {error.get('message', 'Unknown error')}",
                        code=error.get('code', -32000),
                        data=error
                    )
                
                return result.get("result")
                
            except httpx.HTTPError as e:
                last_error = NetworkError(f"Network error: {str(e)}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    continue
                break
            except json.JSONDecodeError as e:
                last_error = BitcoinRPCError(f"Invalid JSON response: {str(e)}")
                break
        
        raise last_error
    
    # Blockchain Information Methods
    async def get_blockchain_info(self) -> Dict[str, Any]:
        """Get blockchain information."""
        return await self._make_request("getblockchaininfo")
    
    async def get_network_info(self) -> Dict[str, Any]:
        """Get network information."""
        return await self._make_request("getnetworkinfo")
    
    async def get_mempool_info(self) -> Dict[str, Any]:
        """Get mempool information."""
        return await self._make_request("getmempoolinfo")
    
    async def get_mining_info(self) -> Dict[str, Any]:
        """Get mining information."""
        return await self._make_request("getmininginfo")
    
    # Block Methods
    async def get_block_count(self) -> int:
        """Get current block count."""
        return await self._make_request("getblockcount")
    
    async def get_block_hash(self, height: int) -> str:
        """Get block hash by height."""
        return await self._make_request("getblockhash", [height])
    
    async def get_block(self, block_hash: str, verbosity: int = 1) -> Dict[str, Any]:
        """Get block by hash."""
        return await self._make_request("getblock", [block_hash, verbosity])
    
    async def get_block_header(self, block_hash: str, verbose: bool = True) -> Dict[str, Any]:
        """Get block header by hash."""
        return await self._make_request("getblockheader", [block_hash, verbose])
    
    # Transaction Methods
    async def get_raw_transaction(self, tx_hash: str, verbose: bool = True) -> Dict[str, Any]:
        """Get raw transaction by hash."""
        return await self._make_request("getrawtransaction", [tx_hash, verbose])
    
    async def get_transaction(self, tx_hash: str) -> Dict[str, Any]:
        """Get transaction by hash (wallet required)."""
        return await self._make_request("gettransaction", [tx_hash])
    
    # Address Methods
    async def validate_address(self, address: str) -> Dict[str, Any]:
        """Validate a Bitcoin address."""
        return await self._make_request("validateaddress", [address])
    
    async def get_address_info(self, address: str) -> Dict[str, Any]:
        """Get address information (wallet required)."""
        return await self._make_request("getaddressinfo", [address])
    
    # UTXO Methods
    async def get_tx_out(self, tx_hash: str, vout: int, include_mempool: bool = True) -> Optional[Dict[str, Any]]:
        """Get transaction output information."""
        return await self._make_request("gettxout", [tx_hash, vout, include_mempool])
    
    async def get_tx_out_set_info(self) -> Dict[str, Any]:
        """Get UTXO set information."""
        return await self._make_request("gettxoutsetinfo")
    
    # Fee Estimation
    async def estimate_smart_fee(self, conf_target: int = 6) -> Dict[str, Any]:
        """Estimate smart fee for confirmation target."""
        return await self._make_request("estimatesmartfee", [conf_target])