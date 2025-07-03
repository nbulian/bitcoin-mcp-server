### .cursor/rules/bitcoin-error-handling.md

---
description: Error handling and debugging patterns for Bitcoin MCP Server
globs: ["src/**/*.py"]
alwaysApply: false
---

# Bitcoin MCP Server Error Handling Guidelines

## Custom Exception Hierarchy
```python
# Base exception class
class BitcoinMCPError(Exception):
    def __init__(self, message: str, error_code: int = -32000):
        self.message = message
        self.error_code = error_code
        super().__init__(message)
    
    def to_json_rpc_error(self):
        return {
            "code": self.error_code,
            "message": self.message
        }

# Specific error types
class BitcoinRPCError(BitcoinMCPError):
    def __init__(self, message: str):
        super().__init__(message, -32001)

class ValidationError(BitcoinMCPError):
    def __init__(self, message: str, field: str = None):
        self.field = field
        super().__init__(message, -32002)

class RateLimitError(BitcoinMCPError):
    def __init__(self, message: str):
        super().__init__(message, -32004)
```

## Error Handling Patterns
```python
# Standard error handling in tool methods
async def get_block_by_height(self, height: int) -> Dict[str, Any]:
    try:
        # Validate input
        if not isinstance(height, int) or height < 0:
            raise ValidationError("Invalid block height", "height")
        
        # Call Bitcoin RPC
        result = await self.client.get_block_by_height(height)
        return result
        
    except ValidationError:
        raise  # Re-raise validation errors as-is
    except httpx.TimeoutException:
        raise BitcoinRPCError("Bitcoin RPC request timed out")
    except httpx.HTTPError as e:
        raise BitcoinRPCError(f"Bitcoin RPC connection failed: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in get_block_by_height: {str(e)}")
        raise BitcoinRPCError("Internal server error")
```

## Debugging Utilities
```python
def log_bitcoin_rpc_request(method: str, params: dict, response: dict = None, error: Exception = None):
    """Log Bitcoin RPC requests for debugging."""
    log_data = {
        "event": "bitcoin_rpc_call",
        "method": method,
        "params": params,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if response:
        log_data["response_size"] = len(str(response))
        log_data["success"] = True
    
    if error:
        log_data["error"] = str(error)
        log_data["error_type"] = type(error).__name__
        log_data["success"] = False
    
    logger.info(json.dumps(log_data))
```

## Common Error Scenarios
- **Bitcoin RPC Connection**: Node unreachable, authentication failed
- **Rate Limiting**: Too many requests, API limits exceeded
- **Validation**: Invalid addresses, malformed transaction hashes
- **Network Issues**: Timeouts, DNS resolution failures
- **Data Not Found**: Block/transaction doesn't exist

## Error Recovery Strategies
```python
# Retry logic with exponential backoff
async def retry_with_backoff(func, max_retries: int = 3, base_delay: float = 1.0):
    for attempt in range(max_retries):
        try:
            return await func()
        except (httpx.TimeoutException, httpx.HTTPError) as e:
            if attempt == max_retries - 1:
                raise BitcoinRPCError(f"Max retries exceeded: {str(e)}")
            
            delay = base_delay * (2 ** attempt)
            logger.warning(f"Retry {attempt + 1}/{max_retries} after {delay}s delay")
            await asyncio.sleep(delay)
```

## Production Error Monitoring
- Log all errors with context information
- Set up alerts for error rate spikes
- Monitor specific error types (RPC failures, validation errors)
- Track error patterns by method and client
```