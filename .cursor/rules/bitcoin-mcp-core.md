## 1. Core Project Rules

### .cursor/rules/bitcoin-mcp-core.md

---
description: Core development guidelines for Bitcoin MCP Server
globs: ["**/*.py"]
alwaysApply: true
---

# Bitcoin MCP Server Core Development Rules

## Project Architecture
- Follow established structure: `src/` for main code, `tools/` for MCP implementations, `utils/` for utilities
- Use async/await pattern consistently for all I/O operations
- Implement proper error handling with custom exception classes from `src/utils/errors.py`

## Code Organization
- **Main Entry Point**: All JSON-RPC routing in `src/main.py`
- **Tool Modules**: Business logic by domain (blockchain, network, address, market)
- **Configuration**: Centralized in `src/config.py` using Pydantic
- **Utilities**: Reusable functions in `src/utils/`

## Error Handling Pattern
```python
try:
    result = await some_operation()
    return result
except SomeSpecificError as e:
    raise ValidationError(f"Operation failed: {str(e)}", "field_name")
except Exception as e:
    raise BitcoinRPCError(f"Unexpected error: {str(e)}")
```

## Async Context Managers
```python
class NewTool:
    async def __aenter__(self):
        self.client = httpx.AsyncClient()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if hasattr(self, 'client'):
            await self.client.aclose()
```

## Configuration Management
- Add new config parameters in `src/config.py`
- Use Pydantic validators for configuration validation
- Load from environment variables with sensible defaults

## Logging Standards
- Use structured logging with timestamps and levels
- Include context information in log messages
- Use appropriate log levels (DEBUG, INFO, ERROR)

## Method Implementation Template
```python
async def new_method(self, param1: str, param2: int) -> Dict[str, Any]:
    """Method description with clear purpose."""
    # 1. Validate inputs
    if not param1:
        raise ValidationError("Missing parameter", "param1")
    
    # 2. Implementation
    result = await self.client.some_rpc_call(param1, param2)
    return result
```
