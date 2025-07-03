"""Address analysis and UTXO management tools."""

from typing import Dict, Any, Optional, List
import httpx
from ..bitcoin_client import BitcoinRPCClient
from ..utils.validation import validate_bitcoin_address
from ..utils.errors import ValidationError
from ..config import config

class AddressTools:
    """Bitcoin address analysis tools."""
    
    def __init__(self, client: BitcoinRPCClient):
        self.client = client
        self.external_client = httpx.AsyncClient(timeout=30.0)
    
    async def validate_address(self, address: str) -> Dict[str, Any]:
        """
        Validate a Bitcoin address and get detailed information.
        
        Args:
            address: Bitcoin address to validate
            
        Returns:
            Dict containing address validation results
        """
        if not validate_bitcoin_address(address):
            raise ValidationError(f"Invalid Bitcoin address format: {address}", "address")
        
        try:
            validation_result = await self.client.validate_address(address)
            
            return {
                "address": address,
                "is_valid": validation_result.get("isvalid", False),
                "is_script": validation_result.get("isscript", False),
                "is_witness": validation_result.get("iswitness", False),
                "witness_version": validation_result.get("witness_version"),
                "witness_program": validation_result.get("witness_program"),
                "script_type": validation_result.get("script_type"),
                "address_type": self._determine_address_type(address)
            }
        except Exception as e:
            raise ValidationError(f"Failed to validate address {address}: {str(e)}")
    
    def _determine_address_type(self, address: str) -> str:
        """
        Determine the type of Bitcoin address.
        
        Args:
            address: Bitcoin address
            
        Returns:
            String indicating address type
        """
        if address.startswith('1'):
            return "P2PKH"  # Pay to Public Key Hash
        elif address.startswith('3'):
            return "P2SH"   # Pay to Script Hash
        elif address.startswith('bc1q'):
            return "P2WPKH" # Pay to Witness Public Key Hash (Bech32)
        elif address.startswith('bc1p'):
            return "P2TR"   # Pay to Taproot (Bech32m)
        elif address.startswith(('m', 'n', '2')):
            return "Testnet"
        else:
            return "Unknown"
    
    async def get_address_balance(self, address: str) -> Dict[str, Any]:
        """
        Get address balance using external API (since core node doesn't track arbitrary addresses).
        
        Args:
            address: Bitcoin address
            
        Returns:
            Dict containing balance information
        """
        if not validate_bitcoin_address(address):
            raise ValidationError(f"Invalid Bitcoin address: {address}", "address")
        
        try:
            # Using mempool.space API for address balance
            url = f"{config.MEMPOOL_SPACE_API_URL}/address/{address}"
            
            async with self.external_client as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
            
            return {
                "address": address,
                "balance": {
                    "confirmed": data.get("chain_stats", {}).get("funded_txo_sum", 0) - 
                               data.get("chain_stats", {}).get("spent_txo_sum", 0),
                    "unconfirmed": data.get("mempool_stats", {}).get("funded_txo_sum", 0) - 
                                 data.get("mempool_stats", {}).get("spent_txo_sum", 0),
                    "total": (data.get("chain_stats", {}).get("funded_txo_sum", 0) - 
                             data.get("chain_stats", {}).get("spent_txo_sum", 0)) +
                            (data.get("mempool_stats", {}).get("funded_txo_sum", 0) - 
                             data.get("mempool_stats", {}).get("spent_txo_sum", 0))
                },
                "transaction_count": {
                    "confirmed": data.get("chain_stats", {}).get("tx_count", 0),
                    "unconfirmed": data.get("mempool_stats", {}).get("tx_count", 0),
                    "total": data.get("chain_stats", {}).get("tx_count", 0) + 
                            data.get("mempool_stats", {}).get("tx_count", 0)
                },
                "address_type": self._determine_address_type(address)
            }
        except httpx.HTTPError as e:
            raise ValidationError(f"Failed to fetch balance for address {address}: {str(e)}")
        except Exception as e:
            raise ValidationError(f"Error getting address balance: {str(e)}")
    
    async def get_address_transactions(self, address: str, limit: int = 25) -> Dict[str, Any]:
        """
        Get transaction history for an address.
        
        Args:
            address: Bitcoin address
            limit: Maximum number of transactions to return (max 50)
            
        Returns:
            Dict containing transaction history
        """
        if not validate_bitcoin_address(address):
            raise ValidationError(f"Invalid Bitcoin address: {address}", "address")
        
        if limit <= 0 or limit > 50:
            raise ValidationError("Limit must be between 1 and 50", "limit")
        
        try:
            # Using mempool.space API for transaction history
            url = f"{config.MEMPOOL_SPACE_API_URL}/address/{address}/txs"
            
            async with self.external_client as client:
                response = await client.get(url)
                response.raise_for_status()
                transactions = response.json()
            
            # Limit results
            limited_txs = transactions[:limit] if len(transactions) > limit else transactions
            
            # Process transaction data
            processed_txs = []
            for tx in limited_txs:
                processed_txs.append({
                    "txid": tx.get("txid"),
                    "block_height": tx.get("status", {}).get("block_height"),
                    "block_hash": tx.get("status", {}).get("block_hash"),
                    "block_time": tx.get("status", {}).get("block_time"),
                    "confirmed": tx.get("status", {}).get("confirmed", False),
                    "fee": tx.get("fee"),
                    "value": self._calculate_address_value(tx, address),
                    "size": tx.get("size"),
                    "weight": tx.get("weight")
                })
            
            return {
                "address": address,
                "total_transactions": len(transactions),
                "returned_transactions": len(processed_txs),
                "transactions": processed_txs
            }
        except httpx.HTTPError as e:
            raise ValidationError(f"Failed to fetch transactions for address {address}: {str(e)}")
        except Exception as e:
            raise ValidationError(f"Error getting address transactions: {str(e)}")
    
    def _calculate_address_value(self, tx: Dict[str, Any], address: str) -> Dict[str, int]:
        """
        Calculate the value change for a specific address in a transaction.
        
        Args:
            tx: Transaction data
            address: Address to calculate value for
            
        Returns:
            Dict with input and output values
        """
        input_value = 0
        output_value = 0
        
        # Check inputs
        for vin in tx.get("vin", []):
            if vin.get("prevout", {}).get("scriptpubkey_address") == address:
                input_value += vin.get("prevout", {}).get("value", 0)
        
        # Check outputs
        for vout in tx.get("vout", []):
            if vout.get("scriptpubkey_address") == address:
                output_value += vout.get("value", 0)
        
        return {
            "input": input_value,
            "output": output_value,
            "net": output_value - input_value
        }
    
    async def get_address_utxos(self, address: str) -> Dict[str, Any]:
        """
        Get unspent transaction outputs (UTXOs) for an address.
        
        Args:
            address: Bitcoin address
            
        Returns:
            Dict containing UTXO information
        """
        if not validate_bitcoin_address(address):
            raise ValidationError(f"Invalid Bitcoin address: {address}", "address")
        
        try:
            # Using mempool.space API for UTXOs
            url = f"{config.MEMPOOL_SPACE_API_URL}/address/{address}/utxo"
            
            async with self.external_client as client:
                response = await client.get(url)
                response.raise_for_status()
                utxos = response.json()
            
            total_value = sum(utxo.get("value", 0) for utxo in utxos)
            
            return {
                "address": address,
                "utxo_count": len(utxos),
                "total_value": total_value,
                "utxos": [
                    {
                        "txid": utxo.get("txid"),
                        "vout": utxo.get("vout"),
                        "value": utxo.get("value"),
                        "status": utxo.get("status", {}),
                        "confirmed": utxo.get("status", {}).get("confirmed", False),
                        "block_height": utxo.get("status", {}).get("block_height"),
                        "block_hash": utxo.get("status", {}).get("block_hash"),
                        "block_time": utxo.get("status", {}).get("block_time")
                    }
                    for utxo in utxos
                ]
            }
        except httpx.HTTPError as e:
            raise ValidationError(f"Failed to fetch UTXOs for address {address}: {str(e)}")
        except Exception as e:
            raise ValidationError(f"Error getting address UTXOs: {str(e)}")
    
    async def analyze_address_activity(self, address: str) -> Dict[str, Any]:
        """
        Perform comprehensive analysis of address activity.
        
        Args:
            address: Bitcoin address
            
        Returns:
            Dict containing detailed address analysis
        """
        if not validate_bitcoin_address(address):
            raise ValidationError(f"Invalid Bitcoin address: {address}", "address")
        
        try:
            # Get comprehensive address data
            balance_data = await self.get_address_balance(address)
            tx_data = await self.get_address_transactions(address, 50)
            utxo_data = await self.get_address_utxos(address)
            
            # Calculate activity metrics
            transactions = tx_data.get("transactions", [])
            total_received = sum(
                tx.get("value", {}).get("output", 0) 
                for tx in transactions 
                if tx.get("value", {}).get("output", 0) > 0
            )
            total_sent = sum(
                abs(tx.get("value", {}).get("input", 0)) 
                for tx in transactions 
                if tx.get("value", {}).get("input", 0) > 0
            )
            
            # Find first and last transaction times
            confirmed_txs = [tx for tx in transactions if tx.get("confirmed")]
            first_tx_time = min(tx.get("block_time", 0) for tx in confirmed_txs) if confirmed_txs else None
            last_tx_time = max(tx.get("block_time", 0) for tx in confirmed_txs) if confirmed_txs else None
            
            return {
                "address": address,
                "address_type": self._determine_address_type(address),
                "summary": {
                    "current_balance": balance_data.get("balance", {}).get("total", 0),
                    "total_received": total_received,
                    "total_sent": total_sent,
                    "transaction_count": balance_data.get("transaction_count", {}).get("total", 0),
                    "utxo_count": utxo_data.get("utxo_count", 0),
                    "first_transaction": first_tx_time,
                    "last_transaction": last_tx_time
                },
                "balance_details": balance_data.get("balance", {}),
                "recent_activity": {
                    "last_10_transactions": transactions[:10],
                    "pending_transactions": [
                        tx for tx in transactions[:10] 
                        if not tx.get("confirmed")
                    ]
                },
                "utxo_analysis": {
                    "total_utxos": utxo_data.get("utxo_count", 0),
                    "total_utxo_value": utxo_data.get("total_value", 0),
                    "largest_utxo": max(
                        utxo_data.get("utxos", []), 
                        key=lambda x: x.get("value", 0),
                        default={}
                    ).get("value", 0) if utxo_data.get("utxos") else 0
                }
            }
        except Exception as e:
            raise ValidationError(f"Failed to analyze address {address}: {str(e)}")
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if hasattr(self, 'external_client'):
            await self.external_client.aclose()                