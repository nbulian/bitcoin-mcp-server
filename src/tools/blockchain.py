"""Blockchain-related MCP tools."""

from typing import Dict, Any, Optional
from ..bitcoin_client import BitcoinRPCClient
from ..utils.validation import validate_block_hash, validate_block_height, validate_transaction_hash
from ..utils.errors import ValidationError

class BlockchainTools:
    """Bitcoin blockchain query tools."""
    
    def __init__(self, client: BitcoinRPCClient):
        self.client = client
    
    async def get_blockchain_info(self) -> Dict[str, Any]:
        """
        Get comprehensive blockchain information.
        
        Returns:
            Dict containing blockchain stats, current height, difficulty, etc.
        """
        try:
            return await self.client.get_blockchain_info()
        except Exception as e:
            raise ValidationError(f"Failed to get blockchain info: {str(e)}")
    
    async def get_block_by_height(self, height: int, include_transactions: bool = False) -> Dict[str, Any]:
        """
        Get block information by height.
        
        Args:
            height: Block height
            include_transactions: Whether to include full transaction data
            
        Returns:
            Dict containing block information
        """
        if not validate_block_height(height):
            raise ValidationError(f"Invalid block height: {height}", "height")
        
        try:
            # Get block hash from height
            block_hash = await self.client.get_block_hash(height)
            
            # Get block data
            verbosity = 2 if include_transactions else 1
            block_data = await self.client.get_block(block_hash, verbosity)
            
            return block_data
        except Exception as e:
            raise ValidationError(f"Failed to get block at height {height}: {str(e)}")
    
    async def get_block_by_hash(self, block_hash: str, include_transactions: bool = False) -> Dict[str, Any]:
        """
        Get block information by hash.
        
        Args:
            block_hash: Block hash
            include_transactions: Whether to include full transaction data
            
        Returns:
            Dict containing block information
        """
        if not validate_block_hash(block_hash):
            raise ValidationError(f"Invalid block hash: {block_hash}", "block_hash")
        
        try:
            verbosity = 2 if include_transactions else 1
            block_data = await self.client.get_block(block_hash, verbosity)
            return block_data
        except Exception as e:
            raise ValidationError(f"Failed to get block {block_hash}: {str(e)}")
    
    async def get_transaction(self, tx_hash: str) -> Dict[str, Any]:
        """
        Get transaction information by hash.
        
        Args:
            tx_hash: Transaction hash
            
        Returns:
            Dict containing transaction information
        """
        if not validate_transaction_hash(tx_hash):
            raise ValidationError(f"Invalid transaction hash: {tx_hash}", "tx_hash")
        
        try:
            tx_data = await self.client.get_raw_transaction(tx_hash, verbose=True)
            return tx_data
        except Exception as e:
            raise ValidationError(f"Failed to get transaction {tx_hash}: {str(e)}")
    
    async def get_latest_blocks(self, count: int = 10) -> Dict[str, Any]:
        """
        Get latest blocks from the blockchain.
        
        Args:
            count: Number of latest blocks to retrieve (max 50)
            
        Returns:
            Dict containing list of latest blocks
        """
        if count <= 0 or count > 50:
            raise ValidationError("Count must be between 1 and 50", "count")
        
        try:
            current_height = await self.client.get_block_count()
            blocks = []
            
            for i in range(count):
                height = current_height - i
                if height < 0:
                    break
                
                block_hash = await self.client.get_block_hash(height)
                block_data = await self.client.get_block(block_hash, 1)
                
                # Simplified block info
                blocks.append({
                    "height": height,
                    "hash": block_hash,
                    "time": block_data.get("time"),
                    "size": block_data.get("size"),
                    "tx_count": len(block_data.get("tx", [])),
                    "difficulty": block_data.get("difficulty"),
                })
            
            return {
                "current_height": current_height,
                "blocks": blocks
            }
        except Exception as e:
            raise ValidationError(f"Failed to get latest blocks: {str(e)}")
    
    async def search_blocks(self, start_height: int, end_height: int) -> Dict[str, Any]:
        """
        Search blocks within a height range.
        
        Args:
            start_height: Starting block height
            end_height: Ending block height
            
        Returns:
            Dict containing blocks in the range
        """
        if not validate_block_height(start_height) or not validate_block_height(end_height):
            raise ValidationError("Invalid block height range")
        
        if start_height > end_height:
            raise ValidationError("Start height must be less than or equal to end height")
        
        if end_height - start_height > 100:
            raise ValidationError("Range too large, maximum 100 blocks")
        
        try:
            blocks = []
            for height in range(start_height, end_height + 1):
                block_hash = await self.client.get_block_hash(height)
                block_data = await self.client.get_block_header(block_hash, verbose=True)
                
                blocks.append({
                    "height": height,
                    "hash": block_hash,
                    "time": block_data.get("time"),
                    "difficulty": block_data.get("difficulty"),
                    "merkleroot": block_data.get("merkleroot"),
                })
            
            return {
                "start_height": start_height,
                "end_height": end_height,
                "total_blocks": len(blocks),
                "blocks": blocks
            }
        except Exception as e:
            raise ValidationError(f"Failed to search blocks in range {start_height}-{end_height}: {str(e)}")