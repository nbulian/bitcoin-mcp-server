### .cursor/rules/bitcoin-api-patterns.md

---
description: JSON-RPC API development patterns for Bitcoin MCP Server
globs: ["src/tools/*.py", "src/main.py"]
alwaysApply: false
---

# Bitcoin MCP Server API Patterns

## JSON-RPC 2.0 Method Implementation

### Adding New Methods Process
1. **Implement method** in appropriate tool module (`src/tools/`)
2. **Add routing** in `src/main.py` route_method() function
3. **Update method list** in get_server_status()
4. **Add validation** using `src/utils/validation.py`
5. **Include error handling** with custom exceptions

### Method Routing Pattern
```python
elif method == "new_method":
    param1 = params.get("param1")
    param2 = params.get("param2", default_value)
    if not param1:
        raise ValidationError("Missing 'param1' parameter", "param1")
    return await tool_instance.new_method(param1, param2)
```

### Tool Module Structure
```python
class BlockchainTool:
    def __init__(self, client: BitcoinRPCClient):
        self.client = client
    
    async def get_block_by_height(self, height: int) -> Dict[str, Any]:
        """Get block data by height."""
        # Validate input
        if not isinstance(height, int) or height < 0:
            raise ValidationError("Invalid block height", "height")
        
        # Implementation
        try:
            result = await self.client.get_block_by_height(height)
            return result
        except Exception as e:
            raise BitcoinRPCError(f"Failed to get block: {str(e)}")
```

## Available Method Categories
- **Server Management**: get_server_status
- **Blockchain Operations**: get_blockchain_info, get_block_by_height, get_transaction
- **Network Monitoring**: get_network_status, get_mempool_stats, get_mining_info
- **Address Analysis**: validate_address, get_address_balance, analyze_address_activity
- **Market Data**: get_current_price, get_price_history, get_market_stats
```
