# Deploying Bitcoin MCP Server to Render.com

## Prerequisites

1. A Render.com account
2. Your Bitcoin RPC credentials
3. A Git repository with your code

## Deployment Steps

### 1. Push your code to GitHub

```bash
git add .
git commit -m "Add Render deployment configuration"
git push origin main
```

### 2. Connect to Render

1. Go to [render.com](https://render.com) and sign in
2. Click "New +" and select "Web Service"
3. Connect your GitHub repository
4. Select the repository containing your Bitcoin MCP Server

### 3. Configure the Web Service

- **Name:** `bitcoin-mcp-server` (or your preferred name)
- **Environment:** `Python`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `chmod +x start.sh && ./start.sh`

### 4. Set Environment Variables

In the Render dashboard, add these environment variables:

**Required Bitcoin RPC Variables:**
```
BITCOIN_RPC_URL=https://your-bitcoin-node-url/
BITCOIN_RPC_USER=your-username
BITCOIN_RPC_PASSWORD=your-password
```

**Optional Configuration:**
```
DEBUG=false
BITCOIN_NETWORK=mainnet
REQUEST_TIMEOUT=30
MAX_RETRIES=3
RATE_LIMIT_PER_MINUTE=60
MEMPOOL_SPACE_API_URL=https://mempool.space/api
```

### 5. Deploy

Click "Create Web Service" and wait for the deployment to complete.

## Important Notes

### Security
- **Never commit your `.env` file** to Git
- Use Render's environment variables for sensitive data
- Your Bitcoin RPC credentials will be encrypted in Render

### Free Tier Limitations
- Render's free tier has limitations on:
  - Build time (15 minutes)
  - Runtime (spins down after 15 minutes of inactivity)
  - Bandwidth and requests

### Production Considerations
- For production use, consider upgrading to a paid plan
- Set up proper monitoring and logging
- Configure custom domains if needed
- Set up SSL certificates (handled automatically by Render)

## Testing Your Deployment

Once deployed, test your server:

```bash
# Health check
curl https://your-app-name.onrender.com/health

# Test RPC endpoint
curl -X POST https://your-app-name.onrender.com/ \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"get_blockchain_info","params":{}}'
```

## Troubleshooting

### Common Issues

1. **Build fails:** Check the build logs in Render dashboard
2. **Runtime errors:** Check the logs for Python errors
3. **Connection issues:** Verify your Bitcoin RPC credentials
4. **Timeout errors:** Check your Bitcoin node connectivity

### Logs
- View logs in the Render dashboard under your service
- Check both build logs and runtime logs

## Update Your AI Agent Directive

After deployment, update your AI agent directive with the new URL:

```
You are a Bitcoin blockchain assistant with access to a Bitcoin MCP (Model Context Protocol) server. You can query real-time Bitcoin blockchain data, network information, address details, and market data through JSON-RPC calls to the server running at https://your-app-name.onrender.com/.

[Rest of your directive remains the same, just update the URL]
``` 