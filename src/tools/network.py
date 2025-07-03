"""Network monitoring and status tools."""

from typing import Dict, Any
from ..bitcoin_client import BitcoinRPCClient
from ..utils.errors import ValidationError

class NetworkTools:
    """Bitcoin network monitoring tools."""
    
    def __init__(self, client: BitcoinRPCClient):
        self.client = client
    
    async def get_network_status(self) -> Dict[str, Any]:
        """
        Get comprehensive network status information.
        
        Returns:
            Dict containing network status, connections, version info
        """
        try:
            network_info = await self.client.get_network_info()
            blockchain_info = await self.client.get_blockchain_info()
            mempool_info = await self.client.get_mempool_info()
            
            return {
                "network": {
                    "version": network_info.get("version"),
                    "subversion": network_info.get("subversion"),
                    "protocol_version": network_info.get("protocolversion"),
                    "connections": network_info.get("connections"),
                    "connections_in": network_info.get("connections_in"),
                    "connections_out": network_info.get("connections_out"),
                    "network_active": network_info.get("networkactive"),
                    "networks": network_info.get("networks", [])
                },
                "blockchain": {
                    "chain": blockchain_info.get("chain"),
                    "blocks": blockchain_info.get("blocks"),
                    "headers": blockchain_info.get("headers"),
                    "best_block_hash": blockchain_info.get("bestblockhash"),
                    "difficulty": blockchain_info.get("difficulty"),
                    "verification_progress": blockchain_info.get("verificationprogress"),
                    "initial_block_download": blockchain_info.get("initialblockdownload"),
                    "size_on_disk": blockchain_info.get("size_on_disk"),
                    "pruned": blockchain_info.get("pruned")
                },
                "mempool": {
                    "size": mempool_info.get("size"),
                    "bytes": mempool_info.get("bytes"),
                    "usage": mempool_info.get("usage"),
                    "max_mempool": mempool_info.get("maxmempool"),
                    "mempool_min_fee": mempool_info.get("mempoolminfee"),
                    "min_relay_tx_fee": mempool_info.get("minrelaytxfee")
                }
            }
        except Exception as e:
            raise ValidationError(f"Failed to get network status: {str(e)}")
    
    async def get_mempool_stats(self) -> Dict[str, Any]:
        """
        Get detailed mempool statistics.
        
        Returns:
            Dict containing mempool stats and fee information
        """
        try:
            mempool_info = await self.client.get_mempool_info()
            
            # Get fee estimates for different confirmation targets
            fee_estimates = {}
            targets = [1, 3, 6, 12, 24, 144]  # blocks
            
            for target in targets:
                try:
                    fee_data = await self.client.estimate_smart_fee(target)
                    if fee_data.get("feerate") is not None:
                        fee_estimates[f"{target}_blocks"] = {
                            "feerate": fee_data.get("feerate"),
                            "blocks": fee_data.get("blocks")
                        }
                except:
                    # Fee estimation might fail, continue with others
                    continue
            
            return {
                "mempool": mempool_info,
                "fee_estimates": fee_estimates,
                "timestamp": mempool_info.get("time")
            }
        except Exception as e:
            raise ValidationError(f"Failed to get mempool stats: {str(e)}")
    
    async def get_mining_info(self) -> Dict[str, Any]:
        """
        Get mining and difficulty information.
        
        Returns:
            Dict containing mining stats and difficulty info
        """
        try:
            mining_info = await self.client.get_mining_info()
            blockchain_info = await self.client.get_blockchain_info()
            
            return {
                "blocks": mining_info.get("blocks"),
                "current_block_weight": mining_info.get("currentblockweight"),
                "current_block_tx": mining_info.get("currentblocktx"),
                "difficulty": mining_info.get("difficulty"),
                "network_hash_ps": mining_info.get("networkhashps"),
                "pooled_tx": mining_info.get("pooledtx"),
                "chain": mining_info.get("chain"),
                "warnings": mining_info.get("warnings"),
                "median_time": blockchain_info.get("mediantime"),
                "chain_work": blockchain_info.get("chainwork")
            }
        except Exception as e:
            raise ValidationError(f"Failed to get mining info: {str(e)}")
    
    async def get_peer_info(self) -> Dict[str, Any]:
        """
        Get information about connected peers.
        
        Returns:
            Dict containing peer connection information
        """
        try:
            # Note: getpeerinfo might not be available on all nodes
            # This is a placeholder for when it's available
            network_info = await self.client.get_network_info()
            
            return {
                "connection_count": network_info.get("connections", 0),
                "connections_in": network_info.get("connections_in", 0),
                "connections_out": network_info.get("connections_out", 0),
                "network_active": network_info.get("networkactive", False),
                "networks": network_info.get("networks", []),
                "relay_fee": network_info.get("relayfee", 0),
                "incremental_fee": network_info.get("incrementalfee", 0),
                "local_addresses": network_info.get("localaddresses", [])
            }
        except Exception as e:
            raise ValidationError(f"Failed to get peer info: {str(e)}")