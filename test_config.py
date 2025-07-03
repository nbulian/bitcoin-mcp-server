#!/usr/bin/env python3
"""Test script to verify Bitcoin RPC configuration."""

import os
from dotenv import load_dotenv
import httpx
import asyncio

# Load environment variables
load_dotenv()

async def test_bitcoin_rpc():
    """Test Bitcoin RPC connection."""
    
    # Get configuration from environment
    rpc_url = os.getenv('BITCOIN_RPC_URL')
    rpc_user = os.getenv('BITCOIN_RPC_USER')
    rpc_password = os.getenv('BITCOIN_RPC_PASSWORD')
    
    print(f"RPC URL: {rpc_url}")
    print(f"RPC User: {rpc_user}")
    print(f"RPC Password: {rpc_password[:4]}***" if rpc_password else "None")
    
    if not all([rpc_url, rpc_user, rpc_password]):
        print("ERROR: Missing required environment variables")
        return
    
    # Test the connection
    try:
        async with httpx.AsyncClient(
            auth=(rpc_user, rpc_password),  # type: ignore
            timeout=30.0,
            headers={"Content-Type": "application/json"}
        ) as client:
            
            payload = {
                "jsonrpc": "1.0",
                "id": "test",
                "method": "getblockchaininfo",
                "params": []
            }
            
            print(f"\nMaking request to: {rpc_url}")
            response = await client.post(rpc_url, json=payload)  # type: ignore
            
            print(f"Response status: {response.status_code}")
            print(f"Response headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"Response: {result}")
                
                if result.get("error"):
                    print(f"RPC Error: {result['error']}")
                else:
                    print("SUCCESS: Bitcoin RPC connection working!")
            else:
                print(f"HTTP Error: {response.text}")
                
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(test_bitcoin_rpc()) 