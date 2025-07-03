# Bitcoin MCP Server

A comprehensive Model Context Protocol (MCP) server for Bitcoin blockchain connectivity and analysis, providing seamless integration with Bitcoin nodes and external APIs for comprehensive blockchain data access.

## 🏗️ Project Structure

```bash
bitcoin-mcp-server/
├── src/                              # Main source code directory
│   ├── __init__.py                   # Package initialization
│   ├── main.py                       # FastAPI application entry point and routing
│   ├── config.py                     # Configuration management with Pydantic
│   ├── bitcoin_client.py             # Bitcoin RPC client with connection management
│   ├── tools/                        # MCP tool implementations
│   │   ├── __init__.py              # Tools package initialization
│   │   ├── blockchain.py            # Blockchain query tools (blocks, transactions)
│   │   ├── network.py               # Network monitoring tools (mempool, mining)
│   │   ├── address.py               # Address analysis tools (balance, UTXOs)
│   │   └── market.py                # Market data tools (price, stats)
│   └── utils/                        # Utility modules
│       ├── __init__.py              # Utils package initialization
│       ├── validation.py            # Input validation utilities
│       └── errors.py                # Custom error classes and handling
├── requirements.txt                  # Python dependencies
├── Dockerfile                        # Docker container configuration
├── docker-compose.yml               # Docker Compose for easy deployment
├── .env.example                      # Environment variables template
└── README.md                         # Project documentation
```

## 📦 Dependencies

### Core Dependencies
- **FastAPI** (0.104.1): Modern web framework for building APIs
- **Uvicorn** (0.24.0): ASGI server for running FastAPI applications
- **httpx** (0.25.2): Async HTTP client for external API calls
- **Pydantic** (2.5.0): Data validation and settings management
- **python-dotenv** (1.0.0): Environment variable loading

### Bitcoin-Specific Dependencies
- **bitcoinlib** (0.12.0): Bitcoin address validation and encoding utilities
  - Used for validating Bitcoin addresses across different formats (P2PKH, P2SH, Bech32, Bech32m)
  - Provides robust address format checking for mainnet, testnet, and regtest networks

### External API Dependencies
The server integrates with several external APIs to provide comprehensive Bitcoin data:

- **Bitcoin RPC Node**: Primary data source for blockchain information
- **Mempool.space API**: Address balance and transaction history
- **CoinGecko API**: Market price data and statistics
- **Alternative.me API**: Fear & Greed Index for market sentiment

## 📁 File Descriptions

### Core Application Files

**src/main.py**

Purpose: FastAPI application entry point and JSON-RPC request routing

Key Features:

- JSON-RPC 2.0 protocol implementation
- Method routing to appropriate tool handlers
- Global error handling and logging
- Application lifecycle management
- CORS middleware configuration

Developer Notes: This is the main entry point. Add new method routes in the route_method() function.

**src/config.py**

Purpose: Centralized configuration management using Pydantic

Key Features:

- Environment variable loading
- Configuration validation
- Network type enumeration (mainnet, testnet, regtest)
- API endpoints and credentials management

Developer Notes: Add new configuration parameters here. All configs are validated on startup.

**src/bitcoin_client.py**

Purpose: Async Bitcoin RPC client with advanced features

Key Features:

- HTTP connection management with authentication
- Rate limiting and retry logic
- Exponential backoff for failed requests
- JSON-RPC 1.0 protocol implementation for Bitcoin Core
- Context manager for proper resource cleanup

Developer Notes: This handles all Bitcoin node communication. Add new RPC methods as async functions.

### Tool Modules

**src/tools/blockchain.py**

Purpose: Blockchain data retrieval and analysis

Available Methods:

- get_blockchain_info(): Network statistics and status
- get_block_by_height(): Block data by height
- get_block_by_hash(): Block data by hash
- get_transaction(): Transaction details
- get_latest_blocks(): Recent blocks list
- search_blocks(): Block range queries

Developer Notes: Add new blockchain query methods here. Ensure proper validation for all inputs.

**src/tools/network.py**

Purpose: Bitcoin network monitoring and status

Available Methods:

- get_network_status(): Comprehensive network overview
- get_mempool_stats(): Mempool statistics and fee estimates
- get_mining_info(): Mining difficulty and hash rate
- get_peer_info(): Network peer information

Developer Notes: Network tools primarily use Bitcoin RPC. Fee estimation targets can be customized.

**src/tools/address.py**

Purpose: Bitcoin address analysis and UTXO management

Available Methods:

- validate_address(): Address format validation
- get_address_balance(): Balance checking via external APIs
- get_address_transactions(): Transaction history
- get_address_utxos(): Unspent transaction outputs
- analyze_address_activity(): Comprehensive address analysis

Developer Notes: Uses mempool.space API for address data. Bitcoin Core doesn't track arbitrary addresses without wallet functionality.

**src/tools/market.py**

Purpose: Bitcoin market data and price information

Available Methods:

- get_current_price(): Real-time price in various currencies
- get_price_history(): Historical price data
- get_market_stats(): Comprehensive market statistics
- get_fear_greed_index(): Market sentiment indicator

Developer Notes: Uses CoinGecko and Alternative.me APIs. API keys can be added for higher rate limits.

### Utility Modules

**src/utils/validation.py**

Purpose: Input validation for Bitcoin-specific data types

Key Functions:

- validate_bitcoin_address(): Multi-format address validation
- validate_transaction_hash(): 64-character hex validation
- validate_block_hash(): Block hash format validation
- validate_block_height(): Block height range validation

Developer Notes: Add new validation functions here. Uses bitcoinlib for address validation.

**src/utils/errors.py**

Purpose: Custom exception classes and JSON-RPC error formatting

Key Classes:

- BitcoinMCPError: Base exception with JSON-RPC formatting
- BitcoinRPCError: Bitcoin node communication errors
- ValidationError: Input validation failures
- NetworkError: Network connectivity issues
- RateLimitError: Rate limiting violations

Developer Notes: All custom errors should inherit from BitcoinMCPError for consistent handling.

## 🚀 Features

### Core Capabilities

- Blockchain Queries: Complete block and transaction data access
- Network Monitoring: Real-time network status and mempool analysis
- Address Analysis: Balance checking, transaction history, UTXO tracking
- Market Data: Price feeds, historical data, market sentiment
- Rate Limiting: Configurable request rate limiting
- Error Handling: Comprehensive error handling with detailed messages
- Docker Support: Production-ready containerization

### JSON-RPC 2.0 Methods

Server Management

- get_server_status: Server health and connectivity status

Blockchain Operations

- get_blockchain_info: Network statistics
- get_block_by_height: Block data by height
- get_block_by_hash: Block data by hash
- get_transaction: Transaction details
- get_latest_blocks: Recent blocks list
- search_blocks: Block range queries

Network Monitoring

- get_network_status: Network overview
- get_mempool_stats: Mempool and fee data
- get_mining_info: Mining statistics
- get_peer_info: Peer connections

Address Analysis

- validate_address: Address validation
- get_address_balance: Balance inquiry
- get_address_transactions: Transaction history
- get_address_utxos: UTXO listing
- analyze_address_activity: Comprehensive analysis

Market Data

- get_current_price: Current Bitcoin price
- get_price_history: Historical price data
- get_market_stats: Market statistics
- get_fear_greed_index: Market sentiment

## 🔧 Error Handling & Response Codes

### JSON-RPC Error Codes

| Code | Name | Description |
|------|------|-------------|
| -32000 | BitcoinMCPError | General Bitcoin MCP server error |
| -32001 | BitcoinRPCError | Bitcoin node RPC communication error |
| -32002 | ValidationError | Input validation failure |
| -32003 | NetworkError | Network connectivity issue |
| -32004 | RateLimitError | Rate limit exceeded |
| -32600 | Invalid Request | JSON-RPC format error |
| -32601 | Method not found | Unknown method requested |
| -32602 | Invalid params | Invalid method parameters |
| -32603 | Internal error | Server internal error |
| -32700 | Parse error | Invalid JSON format |

### Error Response Format

```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32002,
    "message": "Invalid Bitcoin address format",
    "data": {
      "field": "address"
    }
  },
  "id": 1
}
```

### Rate Limiting

The server implements configurable rate limiting to protect the Bitcoin node:

- **Default**: 60 requests per minute per client
- **Configurable**: Via `RATE_LIMIT_PER_MINUTE` environment variable
- **Error Response**: Returns `-32004` error code when exceeded
- **Implementation**: Sliding window rate limiting in `BitcoinRPCClient`

## 📊 API Response Examples

### Successful Response Format

```json
{
  "jsonrpc": "2.0",
  "result": {
    // Method-specific data
  },
  "id": 1
}
```

### Blockchain Info Response

```json
{
  "jsonrpc": "2.0",
  "result": {
    "chain": "main",
    "blocks": 800000,
    "headers": 800000,
    "bestblockhash": "0000000000000000000...",
    "difficulty": 123456789.123456789,
    "mediantime": 1640995200,
    "verificationprogress": 0.999999,
    "initialblockdownload": false,
    "chainwork": "0000000000000000000...",
    "size_on_disk": 123456789,
    "pruned": false,
    "pruneheight": 0,
    "automatic_pruning": false,
    "prune_target_size": 0,
    "softforks": {...},
    "bip9_softforks": {...},
    "warnings": ""
  },
  "id": 1
}
```

### Address Validation Response

```json
{
  "jsonrpc": "2.0",
  "result": {
    "address": "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
    "is_valid": true,
    "is_script": false,
    "is_witness": false,
    "witness_version": null,
    "witness_program": null,
    "script_type": "pubkeyhash",
    "address_type": "P2PKH"
  },
  "id": 2
}
```

### Market Price Response

```json
{
  "jsonrpc": "2.0",
  "result": {
    "currency": "usd",
    "price": 45000.50,
    "change_24h": 2.5,
    "change_percentage_24h": 5.88,
    "market_cap": 850000000000,
    "volume_24h": 25000000000,
    "last_updated": "2024-01-01T12:00:00Z"
  },
  "id": 3
}
```

## 🛠️ Developer Guide

Adding New Methods

Create the method implementation in the appropriate tool module:

```py
async def new_method(self, param1: str, param2: int) -> Dict[str, Any]:
    """Method description."""
    # Validate inputs
    if not param1:
        raise ValidationError("Missing parameter", "param1")
    
    # Implementation
    result = await self.client.some_rpc_call(param1, param2)
    return result
```

Add method routing in src/main.py:

```py
elif method == "new_method":
    param1 = params.get("param1")
    param2 = params.get("param2", default_value)
    if not param1:
        raise ValidationError("Missing 'param1' parameter", "param1")
    return await tool_instance.new_method(param1, param2)
```

Add method to available methods list in get_server_status():

```py
"available_methods": [
    # ... existing methods
    "new_method",
]
```

## Architecture Patterns

Error Handling Strategy

```py
# Always use custom exceptions for consistent error responses
try:
    result = await some_operation()
    return result
except SomeSpecificError as e:
    raise ValidationError(f"Operation failed: {str(e)}", "field_name")
except Exception as e:
    raise BitcoinRPCError(f"Unexpected error: {str(e)}")
```

Async Context Managers

```py
# Use context managers for resource cleanup
class NewTool:
    async def __aenter__(self):
        self.client = httpx.AsyncClient()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if hasattr(self, 'client'):
            await self.client.aclose()
```

Configuration Management

```py
# Add new config parameters in config.py
class Config(BaseSettings):
    NEW_API_KEY: Optional[str] = None
    NEW_API_URL: str = "https://api.example.com"
    
    @validator('NEW_API_URL')
    def validate_new_api_url(cls, v):
        if not v.startswith('http'):
            raise ValueError('API URL must start with http')
        return v
```

## Testing Strategy

Manual Testing with curl

```bash
# Test blockchain info
curl -X POST http://localhost:8000/ \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "get_blockchain_info",
    "params": {},
    "id": 1
  }'

# Test address validation
curl -X POST http://localhost:8000/ \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "validate_address",
    "params": {"address": "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"},
    "id": 2
  }'

# Test rate limiting
for i in {1..65}; do
  curl -X POST http://localhost:8000/ \
    -H "Content-Type: application/json" \
    -d '{"jsonrpc": "2.0", "method": "get_blockchain_info", "params": {}, "id": '$i'}'
done
```

## Unit Testing Framework

```py
# Example test structure (add to tests/ directory)
import pytest
import httpx
from src.main import app

@pytest.fixture
async def client():
    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        yield client

async def test_get_blockchain_info(client):
    response = await client.post("/", json={
        "jsonrpc": "2.0",
        "method": "get_blockchain_info",
        "params": {},
        "id": 1
    })
    assert response.status_code == 200
    data = response.json()
    assert data["jsonrpc"] == "2.0"
    assert "result" in data

async def test_invalid_method(client):
    response = await client.post("/", json={
        "jsonrpc": "2.0",
        "method": "invalid_method",
        "params": {},
        "id": 1
    })
    assert response.status_code == 200
    data = response.json()
    assert data["error"]["code"] == -32601
```

## Performance Considerations

Rate Limiting Implementation

- Default: 60 requests per minute per client
- Configurable via RATE_LIMIT_PER_MINUTE environment variable
- Implemented in BitcoinRPCClient._check_rate_limit()

Connection Pooling

- HTTP clients use connection pooling automatically
- Bitcoin RPC client reuses connections within context
- External API clients have separate connection pools

## Caching Strategy

```py
# Add caching for expensive operations (future enhancement)
from functools import lru_cache
from datetime import datetime, timedelta

class CachedTool:
    def __init__(self):
        self.cache = {}
        self.cache_ttl = timedelta(minutes=5)
    
    async def cached_method(self, key: str):
        now = datetime.utcnow()
        if key in self.cache:
            data, timestamp = self.cache[key]
            if now - timestamp < self.cache_ttl:
                return data
        
        # Fetch new data
        result = await self.expensive_operation(key)
        self.cache[key] = (result, now)
        return result
```

## Security Best Practices

Environment Variables

```bash
# Never commit sensitive data
BITCOIN_RPC_PASSWORD=your_secure_password
API_KEYS=your_api_keys

# Use different credentials for different environments
BITCOIN_RPC_URL_MAINNET=https://mainnet.node.com/
BITCOIN_RPC_URL_TESTNET=https://testnet.node.com/
```

Input Sanitization

```py
# Always validate and sanitize inputs
def sanitize_input(value: str, max_length: int = 100) -> str:
    if not isinstance(value, str):
        raise ValidationError("Input must be string")
    
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[^\w\-.]', '', value)
    
    if len(sanitized) > max_length:
        raise ValidationError(f"Input too long, max {max_length} characters")
    
    return sanitized
```

## 🚀 Quick Start

Development Setup

Clone and setup:

```bash
git clone <repository-url>
cd bitcoin-mcp-server
cp .env.example .env
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Configure environment variables:

```bash
# Edit .env file with your Bitcoin RPC credentials
BITCOIN_RPC_URL=https://bitcoin.two.nono.casa/
BITCOIN_RPC_USER=user
BITCOIN_RPC_PASSWORD=pass
```

Run development server:

```bash
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

## Production Deployment with Docker

Build and run:

```bash
docker-compose up -d
```
Check health:

```bash
curl http://localhost:8000/health
```

View logs:

```bash
docker-compose logs -f bitcoin-mcp-server
```

### Deploy to Render.com

Create render.yaml:

```yaml
services:
  - type: web
    name: bitcoin-mcp-server
    env: docker
    dockerfilePath: ./Dockerfile
    plan: starter
    envVars:
      - key: PORT
        value: 10000
      - key: BITCOIN_RPC_URL
        value: https://bitcoin.two.nono.casa/
      - key: BITCOIN_RPC_USER
        value: user
      - key: BITCOIN_RPC_PASSWORD
        value: pass
    healthCheckPath: /health
```

Deploy:

- Connect your GitHub repository to Render
- Set environment variables in Render dashboard
- Deploy automatically on git push

## 📊 API Examples

Get Current Bitcoin Price

```json
{
  "jsonrpc": "2.0",
  "method": "get_current_price",
  "params": {"currency": "usd"},
  "id": 1
}
```

Analyze Bitcoin Address

```json
{
  "jsonrpc": "2.0",
  "method": "analyze_address_activity",
  "params": {"address": "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"},
  "id": 2
}
```

Get Latest Blocks

```json
{
  "jsonrpc": "2.0",
  "method": "get_latest_blocks",
  "params": {"count": 5},
  "id": 3
}
```

## 🔧 Configuration Options

| Variable | Default | Description |
|----------|---------|-------------|
| HOST | 0.0.0.0 | Server bind address |
| PORT | 8000 | Server port |
| DEBUG | false | Enable debug logging |
| BITCOIN_RPC_URL | https://bitcoin.two.nono.casa/ | Bitcoin RPC endpoint |
| BITCOIN_RPC_USER | user | Bitcoin RPC username |
| BITCOIN_RPC_PASSWORD | pass | Bitcoin RPC password |
| BITCOIN_NETWORK | mainnet | Network type (mainnet/testnet/regtest) |
| REQUEST_TIMEOUT | 30 | HTTP request timeout (seconds) |
| MAX_RETRIES | 3 | Maximum retry attempts |
| RATE_LIMIT_PER_MINUTE | 60 | Requests per minute limit |
| MEMPOOL_SPACE_API_URL | https://mempool.space/api | Mempool.space API endpoint |
| BLOCKCHAIR_API_KEY | null | Optional Blockchair API key |

## 📈 Monitoring and Logging

Health Check Endpoint

```bash
# Check server health
curl http://localhost:8000/health

# Response format
{
  "status": "healthy",
  "bitcoin_connected": true,
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

Logging Configuration

```bash
# Logs are structured with timestamps and levels
2024-01-01 12:00:00,000 - bitcoin_mcp - INFO - Bitcoin MCP Server started on 0.0.0.0:8000
2024-01-01 12:00:01,000 - bitcoin_mcp - ERROR - Bitcoin RPC Error: Connection refused
2024-01-01 12:00:02,000 - bitcoin_mcp - DEBUG - Rate limit check passed for client
```

Docker Logs

```bash
# View real-time logs
docker-compose logs -f bitcoin-mcp-server

# View last 100 lines
docker-compose logs --tail=100 bitcoin-mcp-server
```

## 🔍 Troubleshooting Guide

Common Issues

Bitcoin RPC Connection Failed

```bash
# Check if Bitcoin node is accessible
curl --user user:pass --data-binary '{"jsonrpc":"1.0","id":"test","method":"getblockchaininfo","params":[]}' \
  -H 'content-type: text/plain;' https://bitcoin.two.nono.casa/

# If this fails, check:
# 1. Network connectivity
# 2. RPC credentials
# 3. Node availability
```

Rate Limit Exceeded

```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32004,
    "message": "Rate limit of 60 requests per minute exceeded"
  },
  "id": 1
}
// Solution: Increase RATE_LIMIT_PER_MINUTE or implement client-side throttling
```

Address Validation Failed

```py
# Common causes:
# 1. Invalid address format
# 2. Wrong network (mainnet address on testnet)
# 3. Unsupported address type

# Debug with validate_address method
{
  "jsonrpc": "2.0",
  "method": "validate_address",
  "params": {"address": "your_address_here"},
  "id": 1
}
```

## Development Debugging

Enable Debug Mode

```py
# In .env file
DEBUG=true

# Or via environment
DEBUG=true python -m uvicorn src.main:app --reload
```

Add Custom Logging

```py
import logging
logger = logging.getLogger(__name__)

async def your_method(self):
    logger.debug(f"Processing request with params: {params}")
    try:
        result = await some_operation()
        logger.info(f"Operation successful: {result}")
        return result
    except Exception as e:
        logger.error(f"Operation failed: {str(e)}", exc_info=True)
        raise
```

## Network Security

```py
# Add IP whitelisting for production
ALLOWED_IPS = ["127.0.0.1", "10.0.0.0/8", "192.168.0.0/16"]

@app.middleware("http")
async def ip_whitelist_middleware(request: Request, call_next):
    client_ip = request.client.host
    if client_ip not in ALLOWED_IPS:
        return JSONResponse(
            status_code=403,
            content={"error": "Access denied"}
        )
    return await call_next(request)
```

Input Validation Security

```py
# Implement comprehensive input validation
def validate_amount(amount: Union[str, int, float]) -> float:
    try:
        amount_float = float(amount)
        if amount_float < 0:
            raise ValidationError("Amount cannot be negative")
        if amount_float > 21_000_000:  # Max Bitcoin supply
            raise ValidationError("Amount exceeds maximum Bitcoin supply")
        return amount_float
    except (ValueError, TypeError):
        raise ValidationError("Invalid amount format")

# Sanitize string inputs
def sanitize_string(value: str, max_length: int = 255) -> str:
    if not isinstance(value, str):
        raise ValidationError("Value must be a string")
    
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>"\']', '', value.strip())
    
    if len(sanitized) > max_length:
        raise ValidationError(f"String too long (max {max_length} chars)")
    
    return sanitized

# Validate pagination parameters
def validate_pagination(offset: int = 0, limit: int = 25) -> tuple:
    if offset < 0:
        raise ValidationError("Offset cannot be negative")
    if limit <= 0 or limit > 100:
        raise ValidationError("Limit must be between 1 and 100")
    return offset, limit
```

API Rate Limiting

```py
# Advanced rate limiting with Redis (optional enhancement)
import redis
from datetime import datetime, timedelta

class AdvancedRateLimiter:
    def __init__(self, redis_client):
        self.redis = redis_client
    
    async def check_rate_limit(self, client_id: str, limit: int = 60, window: int = 60):
        key = f"rate_limit:{client_id}"
        current_time = datetime.utcnow()
        
        # Sliding window rate limiting
        pipe = self.redis.pipeline()
        pipe.zremrangebyscore(key, 0, current_time.timestamp() - window)
        pipe.zcard(key)
        pipe.zadd(key, {str(current_time.timestamp()): current_time.timestamp()})
        pipe.expire(key, window)
        
        results = pipe.execute()
        request_count = results[1]
        
        if request_count >= limit:
            raise RateLimitError(f"Rate limit exceeded: {request_count}/{limit} requests")
```

## 🤝 Contributing

### Development Workflow

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/new-method`
3. **Follow coding standards**:
   - Use async/await patterns consistently
   - Implement proper error handling
   - Add input validation for all parameters
   - Follow the established tool module structure
4. **Add tests** for new functionality
5. **Update documentation** for new methods
6. **Submit a pull request**

### Code Style Guidelines

- **Python**: Follow PEP 8 with async/await patterns
- **Error Handling**: Use custom exceptions from `src/utils/errors.py`
- **Validation**: Implement input validation using `src/utils/validation.py`
- **Documentation**: Add docstrings for all public methods
- **Type Hints**: Use type hints for all function parameters and return values

### Testing Guidelines

- **Unit Tests**: Test individual methods and error conditions
- **Integration Tests**: Test JSON-RPC request/response cycles
- **Error Testing**: Test all error conditions and edge cases
- **Rate Limiting**: Test rate limiting behavior
- **Validation**: Test input validation for all parameters

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Bitcoin Core** for the RPC interface
- **Mempool.space** for address and transaction data
- **CoinGecko** for market price data
- **Alternative.me** for Fear & Greed Index
- **FastAPI** for the excellent web framework
- **Pydantic** for data validation and settings management

