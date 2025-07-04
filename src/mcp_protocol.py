"""MCP Protocol implementation for Bitcoin MCP Server."""

from typing import Dict, Any, List, Optional
from .utils.errors import BitcoinMCPError, ValidationError

# MCP Tool Definitions
TOOLS = {
    "get_blockchain_info": {
        "name": "get_blockchain_info",
        "description": "Get comprehensive blockchain information including current height, difficulty, and network status",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    "get_block_by_height": {
        "name": "get_block_by_height",
        "description": "Get block information by height with optional transaction details",
        "inputSchema": {
            "type": "object",
            "properties": {
                "height": {
                    "type": "integer",
                    "description": "Block height to retrieve"
                },
                "include_transactions": {
                    "type": "boolean",
                    "description": "Whether to include full transaction data",
                    "default": False
                }
            },
            "required": ["height"]
        }
    },
    "get_block_by_hash": {
        "name": "get_block_by_hash",
        "description": "Get block information by hash with optional transaction details",
        "inputSchema": {
            "type": "object",
            "properties": {
                "block_hash": {
                    "type": "string",
                    "description": "Block hash to retrieve"
                },
                "include_transactions": {
                    "type": "boolean",
                    "description": "Whether to include full transaction data",
                    "default": False
                }
            },
            "required": ["block_hash"]
        }
    },
    "get_transaction": {
        "name": "get_transaction",
        "description": "Get detailed transaction information by hash",
        "inputSchema": {
            "type": "object",
            "properties": {
                "tx_hash": {
                    "type": "string",
                    "description": "Transaction hash to retrieve"
                }
            },
            "required": ["tx_hash"]
        }
    },
    "get_latest_blocks": {
        "name": "get_latest_blocks",
        "description": "Get the latest blocks from the blockchain",
        "inputSchema": {
            "type": "object",
            "properties": {
                "count": {
                    "type": "integer",
                    "description": "Number of latest blocks to retrieve (max 50)",
                    "default": 10,
                    "minimum": 1,
                    "maximum": 50
                }
            }
        }
    },
    "search_blocks": {
        "name": "search_blocks",
        "description": "Search blocks within a height range",
        "inputSchema": {
            "type": "object",
            "properties": {
                "start_height": {
                    "type": "integer",
                    "description": "Starting block height"
                },
                "end_height": {
                    "type": "integer",
                    "description": "Ending block height"
                }
            },
            "required": ["start_height", "end_height"]
        }
    },
    "get_network_status": {
        "name": "get_network_status",
        "description": "Get comprehensive network status and statistics",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    "get_mempool_stats": {
        "name": "get_mempool_stats",
        "description": "Get mempool statistics and fee estimates",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    "get_mining_info": {
        "name": "get_mining_info",
        "description": "Get mining difficulty and hash rate information",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    "get_peer_info": {
        "name": "get_peer_info",
        "description": "Get network peer information",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    "validate_address": {
        "name": "validate_address",
        "description": "Validate Bitcoin address format and network",
        "inputSchema": {
            "type": "object",
            "properties": {
                "address": {
                    "type": "string",
                    "description": "Bitcoin address to validate"
                }
            },
            "required": ["address"]
        }
    },
    "get_address_balance": {
        "name": "get_address_balance",
        "description": "Get current balance for a Bitcoin address",
        "inputSchema": {
            "type": "object",
            "properties": {
                "address": {
                    "type": "string",
                    "description": "Bitcoin address to check balance for"
                }
            },
            "required": ["address"]
        }
    },
    "get_address_transactions": {
        "name": "get_address_transactions",
        "description": "Get transaction history for a Bitcoin address",
        "inputSchema": {
            "type": "object",
            "properties": {
                "address": {
                    "type": "string",
                    "description": "Bitcoin address to get transactions for"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of transactions to return",
                    "default": 25,
                    "minimum": 1,
                    "maximum": 100
                }
            },
            "required": ["address"]
        }
    },
    "get_address_utxos": {
        "name": "get_address_utxos",
        "description": "Get unspent transaction outputs for a Bitcoin address",
        "inputSchema": {
            "type": "object",
            "properties": {
                "address": {
                    "type": "string",
                    "description": "Bitcoin address to get UTXOs for"
                }
            },
            "required": ["address"]
        }
    },
    "analyze_address_activity": {
        "name": "analyze_address_activity",
        "description": "Analyze address activity patterns and statistics",
        "inputSchema": {
            "type": "object",
            "properties": {
                "address": {
                    "type": "string",
                    "description": "Bitcoin address to analyze"
                }
            },
            "required": ["address"]
        }
    },
    "get_current_price": {
        "name": "get_current_price",
        "description": "Get current Bitcoin price in various currencies",
        "inputSchema": {
            "type": "object",
            "properties": {
                "currency": {
                    "type": "string",
                    "description": "Currency code for price (e.g., usd, eur, gbp)",
                    "default": "usd"
                }
            }
        }
    },
    "get_price_history": {
        "name": "get_price_history",
        "description": "Get historical Bitcoin price data",
        "inputSchema": {
            "type": "object",
            "properties": {
                "days": {
                    "type": "integer",
                    "description": "Number of days of historical data",
                    "default": 7,
                    "minimum": 1,
                    "maximum": 365
                },
                "currency": {
                    "type": "string",
                    "description": "Currency code for price data",
                    "default": "usd"
                }
            }
        }
    },
    "get_market_stats": {
        "name": "get_market_stats",
        "description": "Get comprehensive market statistics",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    "get_fear_greed_index": {
        "name": "get_fear_greed_index",
        "description": "Get Bitcoin Fear & Greed Index for market sentiment",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
}

# MCP Resource Definitions
RESOURCES = {
    "bitcoin:blockchain:info": {
        "uri": "bitcoin:blockchain:info",
        "name": "Bitcoin Blockchain Information",
        "description": "Current blockchain status and statistics",
        "mimeType": "application/json"
    },
    "bitcoin:network:status": {
        "uri": "bitcoin:network:status", 
        "name": "Bitcoin Network Status",
        "description": "Current network status and peer information",
        "mimeType": "application/json"
    },
    "bitcoin:market:stats": {
        "uri": "bitcoin:market:stats",
        "name": "Bitcoin Market Statistics", 
        "description": "Current market statistics and price data",
        "mimeType": "application/json"
    }
}

class MCPProtocol:
    """MCP Protocol implementation."""
    
    def __init__(self, blockchain_tools, network_tools, address_tools, market_tools):
        self.blockchain_tools = blockchain_tools
        self.network_tools = network_tools
        self.address_tools = address_tools
        self.market_tools = market_tools
    
    async def initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize the MCP server."""
        client_info = params.get("clientInfo", {})
        protocol_version = params.get("protocolVersion", "2024-11-05")
        
        return {
            "protocolVersion": protocol_version,
            "capabilities": {
                "tools": {},
                "resources": {}
            },
            "serverInfo": {
                "name": "Bitcoin MCP Server",
                "version": "1.0.0"
            }
        }
    
    async def list_tools(self) -> Dict[str, Any]:
        """List available tools."""
        tools_list = []
        
        # Add blockchain tools if available
        if self.blockchain_tools:
            blockchain_tools = [
                "get_blockchain_info", "get_block_by_height", "get_block_by_hash",
                "get_transaction", "get_latest_blocks", "search_blocks"
            ]
            for tool_name in blockchain_tools:
                if tool_name in TOOLS:
                    tools_list.append(TOOLS[tool_name])
        
        # Add network tools if available
        if self.network_tools:
            network_tools = [
                "get_network_status", "get_mempool_stats", "get_mining_info", "get_peer_info"
            ]
            for tool_name in network_tools:
                if tool_name in TOOLS:
                    tools_list.append(TOOLS[tool_name])
        
        # Add address tools if available
        if self.address_tools:
            address_tools = [
                "validate_address", "get_address_balance", "get_address_transactions",
                "get_address_utxos", "analyze_address_activity"
            ]
            for tool_name in address_tools:
                if tool_name in TOOLS:
                    tools_list.append(TOOLS[tool_name])
        
        # Add market tools if available
        if self.market_tools:
            market_tools = [
                "get_current_price", "get_price_history", "get_market_stats", "get_fear_greed_index"
            ]
            for tool_name in market_tools:
                if tool_name in TOOLS:
                    tools_list.append(TOOLS[tool_name])
        
        return {"tools": tools_list}
    
    async def call_tool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool call."""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if not tool_name:
            raise ValidationError("Missing tool name", "name")
        
        if tool_name not in TOOLS:
            raise ValidationError(f"Unknown tool: {tool_name}", "name")
        
        # Route to appropriate tool handler
        try:
            if tool_name == "get_blockchain_info":
                if not self.blockchain_tools:
                    raise ValidationError("Blockchain tools not available")
                result = await self.blockchain_tools.get_blockchain_info()
            
            elif tool_name == "get_block_by_height":
                if not self.blockchain_tools:
                    raise ValidationError("Blockchain tools not available")
                height = arguments.get("height")
                include_transactions = arguments.get("include_transactions", False)
                if height is None:
                    raise ValidationError("Missing 'height' parameter", "height")
                result = await self.blockchain_tools.get_block_by_height(height, include_transactions)
            
            elif tool_name == "get_block_by_hash":
                if not self.blockchain_tools:
                    raise ValidationError("Blockchain tools not available")
                block_hash = arguments.get("block_hash")
                include_transactions = arguments.get("include_transactions", False)
                if not block_hash:
                    raise ValidationError("Missing 'block_hash' parameter", "block_hash")
                result = await self.blockchain_tools.get_block_by_hash(block_hash, include_transactions)
            
            elif tool_name == "get_transaction":
                if not self.blockchain_tools:
                    raise ValidationError("Blockchain tools not available")
                tx_hash = arguments.get("tx_hash")
                if not tx_hash:
                    raise ValidationError("Missing 'tx_hash' parameter", "tx_hash")
                result = await self.blockchain_tools.get_transaction(tx_hash)
            
            elif tool_name == "get_latest_blocks":
                if not self.blockchain_tools:
                    raise ValidationError("Blockchain tools not available")
                count = arguments.get("count", 10)
                result = await self.blockchain_tools.get_latest_blocks(count)
            
            elif tool_name == "search_blocks":
                if not self.blockchain_tools:
                    raise ValidationError("Blockchain tools not available")
                start_height = arguments.get("start_height")
                end_height = arguments.get("end_height")
                if start_height is None or end_height is None:
                    raise ValidationError("Missing 'start_height' or 'end_height' parameter")
                result = await self.blockchain_tools.search_blocks(start_height, end_height)
            
            # Network tools
            elif tool_name == "get_network_status":
                if not self.network_tools:
                    raise ValidationError("Network tools not available")
                result = await self.network_tools.get_network_status()
            
            elif tool_name == "get_mempool_stats":
                if not self.network_tools:
                    raise ValidationError("Network tools not available")
                result = await self.network_tools.get_mempool_stats()
            
            elif tool_name == "get_mining_info":
                if not self.network_tools:
                    raise ValidationError("Network tools not available")
                result = await self.network_tools.get_mining_info()
            
            elif tool_name == "get_peer_info":
                if not self.network_tools:
                    raise ValidationError("Network tools not available")
                result = await self.network_tools.get_peer_info()
            
            # Address tools
            elif tool_name == "validate_address":
                if not self.address_tools:
                    raise ValidationError("Address tools not available")
                address = arguments.get("address")
                if not address:
                    raise ValidationError("Missing 'address' parameter", "address")
                result = await self.address_tools.validate_address(address)
            
            elif tool_name == "get_address_balance":
                if not self.address_tools:
                    raise ValidationError("Address tools not available")
                address = arguments.get("address")
                if not address:
                    raise ValidationError("Missing 'address' parameter", "address")
                result = await self.address_tools.get_address_balance(address)
            
            elif tool_name == "get_address_transactions":
                if not self.address_tools:
                    raise ValidationError("Address tools not available")
                address = arguments.get("address")
                limit = arguments.get("limit", 25)
                if not address:
                    raise ValidationError("Missing 'address' parameter", "address")
                result = await self.address_tools.get_address_transactions(address, limit)
            
            elif tool_name == "get_address_utxos":
                if not self.address_tools:
                    raise ValidationError("Address tools not available")
                address = arguments.get("address")
                if not address:
                    raise ValidationError("Missing 'address' parameter", "address")
                result = await self.address_tools.get_address_utxos(address)
            
            elif tool_name == "analyze_address_activity":
                if not self.address_tools:
                    raise ValidationError("Address tools not available")
                address = arguments.get("address")
                if not address:
                    raise ValidationError("Missing 'address' parameter", "address")
                result = await self.address_tools.analyze_address_activity(address)
            
            # Market tools
            elif tool_name == "get_current_price":
                if not self.market_tools:
                    raise ValidationError("Market tools not available")
                currency = arguments.get("currency", "usd")
                result = await self.market_tools.get_current_price(currency)
            
            elif tool_name == "get_price_history":
                if not self.market_tools:
                    raise ValidationError("Market tools not available")
                days = arguments.get("days", 7)
                currency = arguments.get("currency", "usd")
                result = await self.market_tools.get_price_history(days, currency)
            
            elif tool_name == "get_market_stats":
                if not self.market_tools:
                    raise ValidationError("Market tools not available")
                result = await self.market_tools.get_market_stats()
            
            elif tool_name == "get_fear_greed_index":
                if not self.market_tools:
                    raise ValidationError("Market tools not available")
                result = await self.market_tools.get_fear_greed_index()
            
            else:
                raise ValidationError(f"Tool '{tool_name}' not implemented")
            
            return {"content": result}
            
        except Exception as e:
            if isinstance(e, BitcoinMCPError):
                raise e
            else:
                raise ValidationError(f"Error executing tool '{tool_name}': {str(e)}")
    
    async def list_resources(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List available resources."""
        resources_list = []
        
        # Add blockchain resources if available
        if self.blockchain_tools:
            resources_list.append(RESOURCES["bitcoin:blockchain:info"])
        
        # Add network resources if available
        if self.network_tools:
            resources_list.append(RESOURCES["bitcoin:network:status"])
        
        # Add market resources if available
        if self.market_tools:
            resources_list.append(RESOURCES["bitcoin:market:stats"])
        
        return {"resources": resources_list}
    
    async def read_resource(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Read resource content."""
        uri = params.get("uri")
        
        if not uri:
            raise ValidationError("Missing resource URI", "uri")
        
        if uri not in RESOURCES:
            raise ValidationError(f"Unknown resource: {uri}", "uri")
        
        try:
            if uri == "bitcoin:blockchain:info":
                if not self.blockchain_tools:
                    raise ValidationError("Blockchain tools not available")
                content = await self.blockchain_tools.get_blockchain_info()
            
            elif uri == "bitcoin:network:status":
                if not self.network_tools:
                    raise ValidationError("Network tools not available")
                content = await self.network_tools.get_network_status()
            
            elif uri == "bitcoin:market:stats":
                if not self.market_tools:
                    raise ValidationError("Market tools not available")
                content = await self.market_tools.get_market_stats()
            
            else:
                raise ValidationError(f"Resource '{uri}' not implemented")
            
            return {
                "contents": [{
                    "uri": uri,
                    "mimeType": RESOURCES[uri]["mimeType"],
                    "text": str(content)
                }]
            }
            
        except Exception as e:
            if isinstance(e, BitcoinMCPError):
                raise e
            else:
                raise ValidationError(f"Error reading resource '{uri}': {str(e)}") 