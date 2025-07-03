"""Main FastAPI application for Bitcoin MCP Server."""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from typing import Dict, Any
from datetime import datetime

from .config import config
from .bitcoin_client import BitcoinRPCClient
from .tools.blockchain import BlockchainTools
from .tools.network import NetworkTools
from .tools.address import AddressTools
from .tools.market import MarketTools
from .utils.errors import BitcoinMCPError, ValidationError

# Configure logging
logging.basicConfig(
    level=logging.INFO if not config.DEBUG else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global tool instances
bitcoin_client = None
blockchain_tools = None
network_tools = None
address_tools = None
market_tools = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global bitcoin_client, blockchain_tools, network_tools, address_tools, market_tools
    
    # Startup
    logger.info("Starting Bitcoin MCP Server...")
    
    try:
        bitcoin_client = BitcoinRPCClient()
        await bitcoin_client.__aenter__()
        
        blockchain_tools = BlockchainTools(bitcoin_client)
        network_tools = NetworkTools(bitcoin_client)
        address_tools = AddressTools(bitcoin_client)
        market_tools = MarketTools()
        
        logger.info("Bitcoin RPC client initialized successfully")
    except Exception as e:
        logger.warning(f"Failed to initialize Bitcoin RPC client: {e}")
        logger.info("Server will start without Bitcoin RPC connectivity")
        bitcoin_client = None
        blockchain_tools = None
        network_tools = None
        address_tools = None
        market_tools = None
    
    logger.info(f"Bitcoin MCP Server started on {config.HOST}:{config.PORT}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Bitcoin MCP Server...")
    
    if bitcoin_client:
        try:
            await bitcoin_client.__aexit__(None, None, None)
        except Exception as e:
            logger.warning(f"Error during Bitcoin client shutdown: {e}")
    
    logger.info("Bitcoin MCP Server shutdown complete")

app = FastAPI(
    title="Bitcoin MCP Server",
    description="Model Context Protocol server for Bitcoin blockchain connectivity and analysis",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for web compatibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(BitcoinMCPError)
async def bitcoin_mcp_exception_handler(request: Request, exc: BitcoinMCPError):
    """Handle Bitcoin MCP specific errors."""
    logger.error(f"Bitcoin MCP Error: {exc.message}")
    return JSONResponse(
        status_code=400,
        content={
            "jsonrpc": "2.0",
            "error": exc.to_json_rpc_error(),
            "id": getattr(request.state, 'request_id', None)
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "jsonrpc": "2.0",
            "error": {
                "code": -32603,
                "message": "Internal error"
            },
            "id": getattr(request.state, 'request_id', None)
        }
    )

@app.post("/")
async def handle_rpc(request: Request):
    """Handle JSON-RPC requests."""
    try:
        body = await request.json()
    except Exception:
        return JSONResponse(
            status_code=400,
            content={
                "jsonrpc": "2.0",
                "error": {
                    "code": -32700,
                    "message": "Parse error"
                },
                "id": None
            }
        )

    # Validate JSON-RPC format
    if body.get("jsonrpc") != "2.0":
        return JSONResponse(
            status_code=400,
            content={
                "jsonrpc": "2.0",
                "error": {
                    "code": -32600,
                    "message": "Invalid Request"
                },
                "id": body.get("id")
            }
        )

    method = body.get("method")
    params = body.get("params", {})
    request_id = body.get("id")
    
    # Store request ID for error handling
    request.state.request_id = request_id

    try:
        result = await route_method(method, params)
        return {
            "jsonrpc": "2.0",
            "result": result,
            "id": request_id
        }
    except BitcoinMCPError as e:
        return {
            "jsonrpc": "2.0",
            "error": e.to_json_rpc_error(),
            "id": request_id
        }
    except Exception as e:
        logger.error(f"Unexpected error in method {method}: {str(e)}", exc_info=True)
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": -32603,
                "message": "Internal error"
            },
            "id": request_id
        }

async def route_method(method: str, params: Dict[str, Any]) -> Any:
    """Route method calls to appropriate handlers."""
    
    # Server status methods
    if method == "get_server_status":
        return await get_server_status()
    
    # Check if Bitcoin tools are available for blockchain/network/address methods
    if method in ["get_blockchain_info", "get_block_by_height", "get_block_by_hash", 
                  "get_transaction", "get_latest_blocks", "search_blocks",
                  "get_network_status", "get_mempool_stats", "get_mining_info", "get_peer_info",
                  "validate_address", "get_address_balance", "get_address_transactions", 
                  "get_address_utxos", "analyze_address_activity"]:
        if not bitcoin_client or not blockchain_tools or not network_tools or not address_tools:
            raise ValidationError("Bitcoin RPC client not available. Please check your configuration.")
    
    # Check if market tools are available for market methods
    if method in ["get_current_price", "get_price_history", "get_market_stats", "get_fear_greed_index"]:
        if not market_tools:
            raise ValidationError("Market tools not available. Please check your configuration.")
    
    # Blockchain methods
    elif method == "get_blockchain_info":
        return await blockchain_tools.get_blockchain_info()
    
    elif method == "get_block_by_height":
        height = params.get("height")
        include_transactions = params.get("include_transactions", False)
        if height is None:
            raise ValidationError("Missing 'height' parameter", "height")
        return await blockchain_tools.get_block_by_height(height, include_transactions)
    
    elif method == "get_block_by_hash":
        block_hash = params.get("block_hash")
        include_transactions = params.get("include_transactions", False)
        if not block_hash:
            raise ValidationError("Missing 'block_hash' parameter", "block_hash")
        return await blockchain_tools.get_block_by_hash(block_hash, include_transactions)
    
    elif method == "get_transaction":
        tx_hash = params.get("tx_hash")
        if not tx_hash:
            raise ValidationError("Missing 'tx_hash' parameter", "tx_hash")
        return await blockchain_tools.get_transaction(tx_hash)
    
    elif method == "get_latest_blocks":
        count = params.get("count", 10)
        return await blockchain_tools.get_latest_blocks(count)
    
    elif method == "search_blocks":
        start_height = params.get("start_height")
        end_height = params.get("end_height")
        if start_height is None or end_height is None:
            raise ValidationError("Missing 'start_height' or 'end_height' parameter")
        return await blockchain_tools.search_blocks(start_height, end_height)
    
    # Network methods
    elif method == "get_network_status":
        return await network_tools.get_network_status()
    
    elif method == "get_mempool_stats":
        return await network_tools.get_mempool_stats()
    
    elif method == "get_mining_info":
        return await network_tools.get_mining_info()
    
    elif method == "get_peer_info":
        return await network_tools.get_peer_info()
    
    # Address methods
    elif method == "validate_address":
        address = params.get("address")
        if not address:
            raise ValidationError("Missing 'address' parameter", "address")
        return await address_tools.validate_address(address)
    
    elif method == "get_address_balance":
        address = params.get("address")
        if not address:
            raise ValidationError("Missing 'address' parameter", "address")
        return await address_tools.get_address_balance(address)
    
    elif method == "get_address_transactions":
        address = params.get("address")
        limit = params.get("limit", 25)
        if not address:
            raise ValidationError("Missing 'address' parameter", "address")
        return await address_tools.get_address_transactions(address, limit)
    
    elif method == "get_address_utxos":
        address = params.get("address")
        if not address:
            raise ValidationError("Missing 'address' parameter", "address")
        return await address_tools.get_address_utxos(address)
    
    elif method == "analyze_address_activity":
        address = params.get("address")
        if not address:
            raise ValidationError("Missing 'address' parameter", "address")
        return await address_tools.analyze_address_activity(address)
    
    # Market methods
    elif method == "get_current_price":
        currency = params.get("currency", "usd")
        return await market_tools.get_current_price(currency)
    
    elif method == "get_price_history":
        days = params.get("days", 7)
        currency = params.get("currency", "usd")
        return await market_tools.get_price_history(days, currency)
    
    elif method == "get_market_stats":
        return await market_tools.get_market_stats()
    
    elif method == "get_fear_greed_index":
        return await market_tools.get_fear_greed_index()
    
    # Unknown method
    else:
        raise ValidationError(f"Method '{method}' not found")

async def get_server_status() -> Dict[str, Any]:
    """Get server status and connectivity information."""
    if not bitcoin_client:
        bitcoin_connected = False
        bitcoin_status = {
            "connected": False,
            "error": "Bitcoin RPC client not initialized"
        }
    else:
        try:
            # Test Bitcoin RPC connectivity
            blockchain_info = await bitcoin_client.get_blockchain_info()
            bitcoin_connected = True
            bitcoin_status = {
                "connected": True,
                "chain": blockchain_info.get("chain"),
                "blocks": blockchain_info.get("blocks"),
                "difficulty": blockchain_info.get("difficulty")
            }
        except Exception as e:
            bitcoin_connected = False
            bitcoin_status = {
                "connected": False,
                "error": str(e)
            }
    
    return {
        "server": {
            "name": "Bitcoin MCP Server",
            "version": "1.0.0",
            "uptime": datetime.utcnow().isoformat(),
            "config": {
                "network": config.BITCOIN_NETWORK,
                "rpc_url": config.BITCOIN_RPC_URL.replace(config.BITCOIN_RPC_PASSWORD, "***")
            }
        },
        "bitcoin_node": bitcoin_status,
        "capabilities": {
            "blockchain_queries": True,
            "network_monitoring": True,
            "address_analysis": True,
            "market_data": True,
            "transaction_lookup": True,
            "utxo_tracking": True
        },
        "available_methods": [
            # Server methods
            "get_server_status",
            
            # Blockchain methods
            "get_blockchain_info",
            "get_block_by_height",
            "get_block_by_hash",
            "get_transaction",
            "get_latest_blocks",
            "search_blocks",
            
            # Network methods
            "get_network_status",
            "get_mempool_stats",
            "get_mining_info",
            "get_peer_info",
            
            # Address methods
            "validate_address",
            "get_address_balance",
            "get_address_transactions",
            "get_address_utxos",
            "analyze_address_activity",
            
            # Market methods
            "get_current_price",
            "get_price_history",
            "get_market_stats",
            "get_fear_greed_index"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Simple health check that doesn't require Bitcoin connection
        return {
            "status": "healthy",
            "message": "Bitcoin MCP Server is running",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )

@app.get("/")
async def root():
    """Root endpoint with server information."""
    return {
        "name": "Bitcoin MCP Server",
        "version": "1.0.0",
        "description": "Model Context Protocol server for Bitcoin blockchain connectivity and analysis",
        "endpoints": {
            "rpc": "POST /",
            "health": "GET /health",
            "info": "GET /"
        },
        "documentation": "Send JSON-RPC 2.0 requests to the root endpoint"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.DEBUG,
        log_level="info" if not config.DEBUG else "debug"
    )